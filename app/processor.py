# app/processor.py
from pdfminer.high_level import extract_text as extract_pdf
from docx import Document
import pytesseract
from PIL import Image
import tempfile

def extract_from_pdf(path: str) -> str:
    return extract_pdf(path)

def extract_from_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_from_image(path: str) -> str:
    return pytesseract.image_to_string(Image.open(path))
