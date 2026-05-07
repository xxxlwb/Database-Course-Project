from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TopicIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: Optional[str] = None


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_archived: Optional[bool] = None


class TopicOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    doc_count: int
    blueprint_status: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
