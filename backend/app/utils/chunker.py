from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings

def chunk_documents(pages: List[Dict]) -> List[Dict]:
    """
    Semantic-aware recursive chunking with metadata preservation.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = []
    chunk_id = 0

    for page in pages:
        splits = splitter.split_text(page["text"])
        for split in splits:
            if len(split.strip()) > 30:
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": split.strip(),
                    "source": page["source"],
                    "page_num": page["page_num"],
                    "total_pages": page["total_pages"],
                })
                chunk_id += 1

    return chunks