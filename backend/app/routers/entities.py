import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db, engine
from ..deps import get_current_user, CurrentUser
from ..schemas.entities import EntityIn, EntityUpdate, EntityOut, AliasIn, MergeIn

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("", response_model=List[EntityOut])
def list_entities(topic_id: Optional[int] = Query(None),
                  q: Optional[str] = Query(None),
                  entity_type: Optional[str] = Query(None),
                  db: Connection = Depends(get_db),
                  u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, topic_id, canonical_name, entity_type, description, "
           "mention_count, created_at FROM entities WHERE 1=1")
    params = {}
    if topic_id:
        sql += " AND topic_id=:tid"; params["tid"] = topic_id
    if q:
        sql += " AND canonical_name LIKE :q"; params["q"] = f"%{q}%"
    if entity_type:
        sql += " AND entity_type=:et"; params["et"] = entity_type
    sql += " ORDER BY mention_count DESC, id DESC LIMIT 500"
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=EntityOut, status_code=201)
def create_entity(payload: EntityIn,
                  db: Connection = Depends(get_db),
                  u: CurrentUser = Depends(get_current_user)):
    try:
        res = db.execute(text(
            "INSERT INTO entities (topic_id, canonical_name, entity_type, description, attributes) "
            "VALUES (:t, :n, :ty, :d, :a)"
        ), {"t": payload.topic_id, "n": payload.canonical_name,
            "ty": payload.entity_type, "d": payload.description,
            "a": json.dumps(payload.attributes) if payload.attributes else None})
    except Exception as e:
        raise HTTPException(409, f"entity exists or invalid: {e}")
    return _get(db, res.lastrowid)


@router.get("/{eid}", response_model=EntityOut)
def get_entity(eid: int, db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    return _get(db, eid)


@router.patch("/{eid}", response_model=EntityOut)
def update_entity(eid: int, payload: EntityUpdate,
                  db: Connection = Depends(get_db),
                  u: CurrentUser = Depends(get_current_user)):
    fields = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if "attributes" in fields:
        fields["attributes"] = json.dumps(fields["attributes"])
    if not fields:
        return _get(db, eid)
    sets = ", ".join(f"{k}=:{k}" for k in fields)
    fields["id"] = eid
    db.execute(text(f"UPDATE entities SET {sets} WHERE id=:id"), fields)
    return _get(db, eid)


@router.delete("/{eid}", status_code=204)
def delete_entity(eid: int, db: Connection = Depends(get_db),
                  u: CurrentUser = Depends(get_current_user)):
    db.execute(text("DELETE FROM entities WHERE id=:id"), {"id": eid})


@router.get("/{eid}/aliases")
def list_aliases(eid: int, db: Connection = Depends(get_db),
                 u: CurrentUser = Depends(get_current_user)):
    rows = db.execute(text(
        "SELECT id, alias, source, confidence, created_at FROM entity_aliases "
        "WHERE entity_id=:id ORDER BY id"
    ), {"id": eid}).mappings().all()
    return [dict(r) for r in rows]


@router.post("/{eid}/aliases", status_code=201)
def add_alias(eid: int, payload: AliasIn,
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    try:
        db.execute(text(
            "INSERT INTO entity_aliases (entity_id, alias, source, confidence) "
            "VALUES (:e, :a, :s, :c)"
        ), {"e": eid, "a": payload.alias, "s": payload.source, "c": payload.confidence})
    except Exception as e:
        raise HTTPException(409, str(e))
    return {"ok": True}


@router.post("/merge", status_code=200)
def merge_entities(payload: MergeIn,
                   db: Connection = Depends(get_db),
                   u: CurrentUser = Depends(get_current_user)):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.callproc("sp_merge_entities", (payload.keep_id, payload.merge_id, u.id))
        raw.commit()
        return {"ok": True, "kept": payload.keep_id}
    except Exception as e:
        raw.rollback()
        raise HTTPException(400, f"merge failed: {e}")
    finally:
        raw.close()


@router.get("/{eid}/neighborhood")
def neighborhood(eid: int, depth: int = Query(2, ge=1, le=5),
                 u: CurrentUser = Depends(get_current_user)):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute("CALL sp_get_entity_neighborhood(%s, %s, @cnt)", (eid, depth))
        rows = cur.fetchall()
        cur.execute("SELECT @cnt")
        cnt = cur.fetchone()[0]
        cur.close()
        return {"count": cnt,
                "nodes": [{"entity_id": r[0], "distance": r[1],
                           "name": r[2], "type": r[3]} for r in rows]}
    finally:
        raw.close()


def _get(db: Connection, eid: int) -> dict:
    row = db.execute(text(
        "SELECT id, topic_id, canonical_name, entity_type, description, "
        "mention_count, created_at FROM entities WHERE id=:id"
    ), {"id": eid}).mappings().first()
    if not row:
        raise HTTPException(404, "entity not found")
    return dict(row)
