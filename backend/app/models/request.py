from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000, description="Medical question")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], max_length=20)
    stream: bool = Field(default=True)