import pdfplumber
from bs4 import BeautifulSoup

def extract_text_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)

def extract_text_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    return soup.get_text(separator=" ")
