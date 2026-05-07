from fastapi import APIRouter, Depends, HTTPException
from ..db import engine
from ..deps import require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/recompute-mentions")
def recompute_mentions(u=Depends(require_role("admin"))):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.callproc("sp_recompute_entity_mentions", ())
        raw.commit()
        return {"ok": True}
    finally:
        raw.close()


@router.post("/archive-inactive-topics")
def archive_inactive(days: int = 30, u=Depends(require_role("admin"))):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute("CALL sp_archive_inactive_topics(%s, @cnt)", (days,))
        cur.execute("SELECT @cnt")
        cnt = cur.fetchone()[0]
        raw.commit()
        return {"ok": True, "archived": cnt}
    finally:
        raw.close()


@router.post("/propagate-rename")
def propagate_rename(topic_id: int, pattern: str, new_name: str,
                     u=Depends(require_role("admin"))):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.callproc("sp_propagate_entity_rename", (topic_id, pattern, new_name))
        raw.commit()
        return {"ok": True}
    finally:
        raw.close()
