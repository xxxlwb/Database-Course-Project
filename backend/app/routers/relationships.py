from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..schemas.relationships import RelationshipIn, RelationshipOut

router = APIRouter(prefix="/api/relationships", tags=["relationships"])


@router.get("", response_model=List[RelationshipOut])
def list_rels(topic_id: Optional[int] = Query(None),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, topic_id, source_entity_id, target_entity_id, relation_type, "
           "description, weight, created_at FROM relationships")
    params = {}
    if topic_id:
        sql += " WHERE topic_id=:t"; params["t"] = topic_id
    sql += " ORDER BY id DESC LIMIT 500"
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=RelationshipOut, status_code=201)
def create_rel(payload: RelationshipIn,
               db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    try:
        res = db.execute(text(
            "INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, "
            "relation_type, description, weight) "
            "VALUES (:t, :s, :d, :rt, :ds, :w)"
        ), {"t": payload.topic_id, "s": payload.source_entity_id,
            "d": payload.target_entity_id, "rt": payload.relation_type,
            "ds": payload.description, "w": payload.weight})
    except Exception as e:
        raise HTTPException(400, f"insert failed (cross-topic / duplicate / self-loop?): {e}")
    row = db.execute(text(
        "SELECT id, topic_id, source_entity_id, target_entity_id, relation_type, "
        "description, weight, created_at FROM relationships WHERE id=:id"
    ), {"id": res.lastrowid}).mappings().first()
    return dict(row)


@router.delete("/{rid}", status_code=204)
def delete_rel(rid: int, db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    db.execute(text("DELETE FROM relationships WHERE id=:id"), {"id": rid})
