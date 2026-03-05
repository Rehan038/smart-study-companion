import fitz
from pathlib import Path

def extract_text_from_pdf(file_path):
    """Extract full text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(str(file_path))
        if doc.page_count == 0:
            raise ValueError("PDF is empty")
        text = "\n".join(page.get_text() for page in doc).strip()
        doc.close()
        if not text:
            raise ValueError("No text could be extracted")
        return text
    except Exception as e:
        raise RuntimeError(f"Error processing PDF: {str(e)}")
