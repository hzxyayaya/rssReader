from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AskRequest(BaseModel):
    question: str
    session_id: Optional[str] = None  # UUID
    
    # Context filters - can be combined
    article_id: Optional[int] = None           # Single article (legacy)
    article_ids: Optional[List[int]] = None    # Multiple specific articles
    feed_ids: Optional[List[int]] = None       # Filter by subscription sources
    date_filter: Optional[str] = None          # "today", "yesterday", "week", "all"


class Citation(BaseModel):
    text: str
    source_id: Optional[int] = None

class AnswerResponse(BaseModel):
    answer: str
    session_id: str
    citations: List[Dict[str, Any]] = []

class MessageSchema(BaseModel):
    role: str
    content: str
    created_at: Any
    
    class Config:
        from_attributes = True
