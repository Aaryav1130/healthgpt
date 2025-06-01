import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict
import re

def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, str]]:
    """
    Extract text from PDF with page metadata.
    Returns list of {page_num, text, source} dicts.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        # Clean text: remove excessive whitespace, fix hyphens
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'(?<=[a-z])-\s+(?=[a-z])', '', text)  # fix word breaks

        if len(text) > 50:  # skip near-empty pages
            pages.append({
                "page_num": page_num,
                "text": text,
                "source": Path(pdf_path).name,
                "total_pages": len(doc)
            })

    doc.close()
    return pages