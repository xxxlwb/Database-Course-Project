import json
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import engine, get_db
from ..deps import require_role
from ..services.sql_console import execute_one
from ..config import settings
from ..schemas.dev import SqlIn

router = APIRouter(prefix="/api/dev", tags=["dev"])


def _safe(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (bytes, bytearray)):
        return v.hex()
    return v


@router.post("/sql/execute")
def sql_execute(payload: SqlIn, request: Request,
                u=Depends(require_role("admin")),
                db: Connection = Depends(get_db)):
    if not settings.sql_console_enabled:
        raise HTTPException(403, "SQL console disabled")
    ip = request.client.host if request.client else "unknown"
    try:
        result = execute_one(engine, payload.sql, payload.max_rows)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        # Log to audit even on failure
        db.execute(text(
            "INSERT INTO audit_logs (user_id, action, entity_type, before_value, ip_address) "
            "VALUES (:u, 'sql_exec_failed', 'sql', :sql, :ip)"
        ), {"u": u.id,
            "sql": json.dumps({"sql": payload.sql, "error": str(e)[:200]}),
            "ip": ip})
        raise HTTPException(400, f"sql error: {e}")

    db.execute(text(
        "INSERT INTO audit_logs (user_id, action, entity_type, before_value, ip_address) "
        "VALUES (:u, 'sql_exec', 'sql', :sql, :ip)"
    ), {"u": u.id,
        "sql": json.dumps({"sql": payload.sql,
                            "kind": result["kind"],
                            "elapsed_ms": result["elapsed_ms"]}),
        "ip": ip})

    # Convert non-JSON-serializable values (datetime, Decimal, bytes)
    if "rows" in result:
        result["rows"] = [[_safe(c) for c in row] for row in result["rows"]]
    return result
