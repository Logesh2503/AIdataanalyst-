import pandas as pd
import fitz  # from PyMuPDF
from docx import Document
import pytesseract
from PIL import Image
import os

def read_file(file_path):
    """
    Reads and returns the content of a file based on its extension.
    Supports CSV, Excel, TXT, DOCX, PDF, and image files.
    """
    try:
        ext = os.path.splitext(file_path)[-1].lower()

        if ext == ".csv":
            return pd.read_csv(file_path)

        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)

        elif ext == ".txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == ".docx":
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])

        elif ext == ".pdf":
            doc = fitz.open(file_path)
            return "\n".join([page.get_text() for page in doc])

        elif ext in [".png", ".jpg", ".jpeg"]:
            return pytesseract.image_to_string(Image.open(file_path))

        else:
            return "❌ Unsupported file type."

    except Exception as e:
        return f"❌ Error reading file: {e}"
