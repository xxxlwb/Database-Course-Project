from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..schemas.topics import TopicIn, TopicUpdate, TopicOut

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("", response_model=List[TopicOut])
def list_topics(db: Connection = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    rows = db.execute(text(
        "SELECT id, name, description, owner_id, doc_count, blueprint_status, "
        "is_archived, created_at, updated_at FROM topics ORDER BY id DESC"
    )).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=TopicOut, status_code=201)
def create_topic(payload: TopicIn, db: Connection = Depends(get_db),
                 u: CurrentUser = Depends(get_current_user)):
    try:
        res = db.execute(text(
            "INSERT INTO topics (name, description, owner_id) VALUES (:n, :d, :o)"
        ), {"n": payload.name, "d": payload.description, "o": u.id})
        tid = res.lastrowid
    except Exception as e:
        raise HTTPException(status.HTTP_409_CONFLICT, f"name conflict: {e}")
    return _get(db, tid)


@router.get("/{topic_id}", response_model=TopicOut)
def get_topic(topic_id: int, db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    return _get(db, topic_id)


@router.patch("/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: int, payload: TopicUpdate,
                 db: Connection = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    fields = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not fields:
        return _get(db, topic_id)
    sets = ", ".join(f"{k}=:{k}" for k in fields)
    fields["id"] = topic_id
    db.execute(text(f"UPDATE topics SET {sets} WHERE id=:id"), fields)
    return _get(db, topic_id)


@router.delete("/{topic_id}", status_code=204)
def delete_topic(topic_id: int, db: Connection = Depends(get_db),
                 u: CurrentUser = Depends(get_current_user)):
    db.execute(text("DELETE FROM topics WHERE id=:id"), {"id": topic_id})


def _get(db: Connection, tid: int) -> dict:
    row = db.execute(text(
        "SELECT id, name, description, owner_id, doc_count, blueprint_status, "
        "is_archived, created_at, updated_at FROM topics WHERE id=:id"
    ), {"id": tid}).mappings().first()
    if not row:
        raise HTTPException(404, "topic not found")
    return dict(row)
