# backend/app/routers/blueprint.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..services.blueprint import regenerate_for_topic

router = APIRouter(prefix="/api/topics", tags=["blueprint"])


@router.post("/{topic_id}/blueprint")
def regen(topic_id: int, db: Connection = Depends(get_db),
          u: CurrentUser = Depends(get_current_user)):
    try:
        return regenerate_for_topic(db, topic_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{topic_id}/blueprint")
def get(topic_id: int, db: Connection = Depends(get_db),
        u: CurrentUser = Depends(get_current_user)):
    row = db.execute(text(
        "SELECT id, canonical_entities, key_patterns, global_timeline, "
        "contributing_doc_count, status, version, generated_at "
        "FROM analysis_blueprints WHERE topic_id=:t"
    ), {"t": topic_id}).mappings().first()
    if not row:
        raise HTTPException(404, "no blueprint")
    return dict(row)
