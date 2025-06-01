from pydantic import BaseModel
from typing import List, Optional

class SourceDocument(BaseModel):
    source: str
    page_num: int
    text: str
    rerank_score: Optional[float]
    retrieval_score: Optional[float]

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    query: str
    total_chunks_retrieved: int