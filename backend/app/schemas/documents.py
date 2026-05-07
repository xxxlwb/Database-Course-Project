from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentIn(BaseModel):
    topic_id: int
    title: str
    source_type: str = "text"
    content: str


class DocumentOut(BaseModel):
    id: int
    topic_id: int
    uploader_id: int
    title: str
    source_type: str
    content: Optional[str]
    chunks_count: int
    status: str
    uploaded_at: datetime


class ChunkOut(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    token_count: Optional[int]
