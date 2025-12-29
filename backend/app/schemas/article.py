from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None

class Article(ArticleBase):
    id: int
    feed_id: int
    content: Optional[str] = None
    is_vectorized: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ArticleList(ArticleBase):
    id: int
    feed_id: int
    # No content in list view
    created_at: datetime
    
    class Config:
        from_attributes = True
