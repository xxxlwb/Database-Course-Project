from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..security import hash_password, verify_password, create_access_token
from ..deps import get_current_user, CurrentUser
from ..schemas.auth import LoginIn, RegisterIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Connection = Depends(get_db)):
    existing = db.execute(text("SELECT id FROM users WHERE username=:u OR email=:e"),
                          {"u": payload.username, "e": payload.email}).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "username or email exists")
    res = db.execute(text(
        "INSERT INTO users (username, password_hash, email, role) "
        "VALUES (:u, :p, :e, 'editor')"
    ), {"u": payload.username, "p": hash_password(payload.password), "e": payload.email})
    uid = res.lastrowid
    tok = create_access_token(uid, "editor")
    return TokenOut(access_token=tok, user={"id": uid, "username": payload.username, "role": "editor"})


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Connection = Depends(get_db)):
    row = db.execute(text("SELECT id, password_hash, role FROM users WHERE username=:u"),
                     {"u": payload.username}).first()
    if not row or not verify_password(payload.password, row[1]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    tok = create_access_token(row[0], row[2])
    return TokenOut(access_token=tok, user={"id": row[0], "username": payload.username, "role": row[2]})


@router.get("/me")
def me(u: CurrentUser = Depends(get_current_user)):
    return {"id": u.id, "username": u.username, "role": u.role}
