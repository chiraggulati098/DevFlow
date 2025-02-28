import os
import pdfplumber

DOCS_DIR = "../docs/"

def extract_text_from_pdf(pdf_path):
    '''
    Extracts and cleans text from a given pdf file
    '''
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n\n"
    
    return text.strip()

def process_and_store_pdf(pdf_path):
    '''
    Extracts text fromm PDF, splits it into paras, and saves processed text
    '''
    text = extract_text_from_pdf(pdf_path)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    return paragraphs