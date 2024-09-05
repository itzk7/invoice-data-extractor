import json
import io
import base64
import boto3
from botocore.exceptions import ClientError
from pdf2image import convert_from_bytes
from PIL.Image import Image, Resampling
import time

invoice_pdf_file_path = 'MultiPageInvoice.pdf'

BEDROCK_ANTHROPIC_VERSION = 'bedrock-2023-05-31'
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
SYSTEM_ROLE = 'You are an Expense Bill Analyst'
USER_PROMPT = '''
    Find the following fields and put it in JSON and don't return any thing else

    total_amount: numeric,
    company_name: str,
    currency_name: str,
    invoice_no: str,
    invoice_date: str

'''

def get_bedrock_runtime() -> any:
    # the below client will work if your local aws config has access to bedrock
    client = boto3.client('bedrock-runtime')
    # pass credentials with bedrock access
    # client = boto3.client('bedrock-runtime', aws_access_key_id='XXXXX',
    #         aws_secret_access_key='XXXXX')
    return client

def run_multi_modal_prompt(req_body: str) -> dict:
    try:
        bedrock_runtime = get_bedrock_runtime()

        response = bedrock_runtime.invoke_model(
            body=req_body, modelId=MODEL_ID)
        response_body = json.loads(response.get('body').read())

        return response_body
    except ClientError as e:
        print('unable to create bedrock runtime', e)
        raise

def split_pdf_pages(pdf_bytes:bytes, max_size:tuple=(1024, 1024)) -> list[str]:
    images = convert_from_bytes(pdf_file=pdf_bytes, fmt='png')

    for img in images:
        # resize if it exceeds the max size
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Resampling.LANCZOS)
    res = list(map(b64_encoded_str, images))

    return res

def b64_encoded_str(img: Image) -> str:
    byte_io = io.BytesIO()
    img.save(fp=byte_io, format='PNG', quality=75, optimize=True)
    # img.save(f'pdf2img_{str(time.time())}.png') <-- uncomment to analyse the image metadata
    return base64.b64encode(byte_io.getvalue()).decode('utf8')


def get_file_bytes(file_path:str) -> bytes:
    with open(file_path, "rb") as file:
        file_bytes = file.read()
    return file_bytes

def build_claude_req_body(file_path:str) -> dict:
    file_bytes = get_file_bytes(file_path)
    base64_encoded_pngs = split_pdf_pages(file_bytes)

    messages = [
        {
            "role": "user",
            "content": [
                *[
                    {
                        "type": "image", 
                        "source": {
                            "type": "base64", 
                            "media_type": "image/png",
                            "data": base64_encoded_png
                            }
                    } for base64_encoded_png in base64_encoded_pngs
                ],
                {
                    "type": "text",
                    "text": USER_PROMPT
                }
            ]
        }
    ]

    req_body = {
            "anthropic_version": BEDROCK_ANTHROPIC_VERSION,
            "messages": messages,
            "system": SYSTEM_ROLE,
            'max_tokens': 100
        }

    return req_body

def extract_data(file_path):
    try:
        body = build_claude_req_body(file_path)
        response = run_multi_modal_prompt(req_body=json.dumps(body))
        print('Model response')
        print(response)
        d = json.loads(response['content'][0]['text'])
        return d
    except Exception as e:
        print('something went wrong', e)
        return {}

result = extract_data(invoice_pdf_file_path)
print(result)
