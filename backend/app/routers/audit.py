from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])


@router.get("")
def list_logs(user_id: Optional[int] = Query(None),
              action: Optional[str] = Query(None),
              limit: int = Query(100, le=500),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, user_id, action, entity_type, entity_id, "
           "before_value, after_value, ip_address, created_at FROM audit_logs WHERE 1=1")
    p = {}
    if user_id:
        sql += " AND user_id=:u"; p["u"] = user_id
    if action:
        sql += " AND action=:a"; p["a"] = action
    sql += " ORDER BY id DESC LIMIT :lim"; p["lim"] = limit
    rows = db.execute(text(sql), p).mappings().all()
    return [dict(r) for r in rows]
