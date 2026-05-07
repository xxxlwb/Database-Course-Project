from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
def list_jobs(topic_id: Optional[int] = Query(None),
              status: Optional[str] = Query(None),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, document_id, topic_id, job_type, status, progress, "
           "result, error_message, created_at, completed_at FROM extraction_jobs WHERE 1=1")
    p = {}
    if topic_id:
        sql += " AND topic_id=:t"; p["t"] = topic_id
    if status:
        sql += " AND status=:s"; p["s"] = status
    sql += " ORDER BY id DESC LIMIT 200"
    rows = db.execute(text(sql), p).mappings().all()
    return [dict(r) for r in rows]


@router.get("/{jid}")
def get_job(jid: int, db: Connection = Depends(get_db),
            u: CurrentUser = Depends(get_current_user)):
    row = db.execute(text(
        "SELECT id, document_id, topic_id, job_type, status, progress, "
        "result, error_message, started_at, completed_at, created_at "
        "FROM extraction_jobs WHERE id=:id"
    ), {"id": jid}).mappings().first()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(404)
    return dict(row)
