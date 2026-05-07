from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class RelationshipIn(BaseModel):
    topic_id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    description: Optional[str] = None
    weight: float = 1.0


class RelationshipOut(BaseModel):
    id: int
    topic_id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    description: Optional[str]
    weight: float
    created_at: datetime
