# backend/app/routers/extract.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..services.extract import extract_for_topic

router = APIRouter(prefix="/api/topics", tags=["extract"])


@router.post("/{topic_id}/extract")
def extract(topic_id: int, doc_id: Optional[int] = Query(None),
            db: Connection = Depends(get_db),
            u: CurrentUser = Depends(get_current_user)):
    try:
        return extract_for_topic(db, topic_id, doc_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
