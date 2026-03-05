from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class IngestRequest(BaseModel):
    urls: List[HttpUrl]

class ContentQueueBase(BaseModel):
    user_id: str
    original_url: str
    platform: Optional[str] = None
    status: str = "Pending"
    source_title: Optional[str] = None
    thumbnail_url: Optional[str] = None

class ContentQueueCreate(ContentQueueBase):
    pass

class ContentQueueResponse(ContentQueueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
