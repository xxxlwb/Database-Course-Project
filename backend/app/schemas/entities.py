from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class EntityIn(BaseModel):
    topic_id: int
    canonical_name: str
    entity_type: str
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class EntityUpdate(BaseModel):
    canonical_name: Optional[str] = None
    entity_type: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class EntityOut(BaseModel):
    id: int
    topic_id: int
    canonical_name: str
    entity_type: str
    description: Optional[str]
    mention_count: int
    created_at: datetime


class AliasIn(BaseModel):
    alias: str
    source: str = "user"
    confidence: float = 1.0


class MergeIn(BaseModel):
    keep_id: int
    merge_id: int
