from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FeedBase(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    icon: Optional[str] = None

class FeedCreate(FeedBase):
    pass

class Feed(FeedBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FeedUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
