# Invoice Data Extractor
A simple setup triggers the Claude sonnet model using Amazon Bedrock to extract invoice data in the form of JSON.
We used the MultiPageInvoice.pdf downloaded from https://resources.docmosis.com/example-templates/generate-multi-page-invoice-from-template

## Requirements

Python version: 3.12

### Python package

* pdf2image
* boto3

Simply run to install python dependencies `pip install -r requirements.txt`

### Poppler setup

pdf2image uses poppler to read pdf page count and other metadata.

For macos, ` brew install poppler`

For Windows machine refer here, https://stackoverflow.com/a/70095504


### AWS permission
* Amazon bedrock
* Claude sonnet 3.5 access(model id: anthropic.claude-3-5-sonnet-20240620-v1:0)

### How to run

If you run the script `python pdf_data.py`, the expected output is:

```
{
  'total_amount': 5715.0, 
  'company_name': 'META LEGAL & FINANCE', 
  'currency_name': 'USD', 
  'invoice_no': '00000135', 
  'invoice_date': '12 March 2024'
}
```

For concepts and code explanation check out this blog, https://blog.tarkalabs.com/extracting-structured-data-from-pdfs-with-claude-sonnet-and-amazon-bedrock-16cc04b6a6fb