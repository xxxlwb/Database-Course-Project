from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Connection
from .db import get_db
from .security import decode_token


class CurrentUser:
    def __init__(self, id: int, username: str, role: str):
        self.id = id
        self.username = username
        self.role = role


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Connection = Depends(get_db),
) -> CurrentUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing token")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    uid = int(payload["sub"])
    row = db.execute(text("SELECT id, username, role FROM users WHERE id=:id"),
                     {"id": uid}).first()
    if not row:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    return CurrentUser(id=row[0], username=row[1], role=row[2])


def require_role(*allowed):
    def checker(u: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if u.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"role required: {allowed}")
        return u
    return checker


def get_client_ip(request_headers: Optional[str] = Header(None, alias="X-Forwarded-For")) -> str:
    return (request_headers or "").split(",")[0].strip() or "unknown"
