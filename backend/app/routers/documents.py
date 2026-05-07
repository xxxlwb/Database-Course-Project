import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..schemas.documents import DocumentIn, DocumentOut, ChunkOut
from ..services.chunker import chunk_text

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=List[DocumentOut])
def list_docs(topic_id: Optional[int] = Query(None),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, topic_id, uploader_id, title, source_type, content, "
           "chunks_count, status, uploaded_at FROM documents")
    params = {}
    if topic_id:
        sql += " WHERE topic_id=:tid"
        params["tid"] = topic_id
    sql += " ORDER BY id DESC LIMIT 200"
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=DocumentOut, status_code=201)
def create_doc(payload: DocumentIn,
               db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    h = hashlib.sha256(payload.content.encode("utf-8")).hexdigest()
    res = db.execute(text(
        "INSERT INTO documents (topic_id, uploader_id, title, source_type, content, "
        "content_hash, file_size) VALUES (:t, :u, :ti, :st, :c, :h, :fs)"
    ), {"t": payload.topic_id, "u": u.id, "ti": payload.title,
        "st": payload.source_type, "c": payload.content, "h": h,
        "fs": len(payload.content.encode())})
    did = res.lastrowid

    chunks = chunk_text(payload.content)
    for idx, c in enumerate(chunks):
        ch = hashlib.sha256(c.encode()).hexdigest()
        db.execute(text(
            "INSERT INTO document_chunks (document_id, chunk_index, content, content_hash, token_count) "
            "VALUES (:d, :i, :c, :h, :t)"
        ), {"d": did, "i": idx, "c": c, "h": ch, "t": len(c)})

    db.execute(text("UPDATE documents SET status='chunk_done' WHERE id=:id"), {"id": did})
    return _get(db, did)


@router.get("/{doc_id}", response_model=DocumentOut)
def get_doc(doc_id: int, db: Connection = Depends(get_db),
            u: CurrentUser = Depends(get_current_user)):
    return _get(db, doc_id)


@router.delete("/{doc_id}", status_code=204)
def delete_doc(doc_id: int, db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    row = db.execute(text("SELECT topic_id FROM documents WHERE id=:id"),
                     {"id": doc_id}).first()
    if row:
        db.execute(text("UPDATE topics SET doc_count = GREATEST(doc_count-1, 0) WHERE id=:t"),
                   {"t": row[0]})
    db.execute(text("DELETE FROM documents WHERE id=:id"), {"id": doc_id})


@router.get("/{doc_id}/chunks", response_model=List[ChunkOut])
def list_chunks(doc_id: int, db: Connection = Depends(get_db),
                u: CurrentUser = Depends(get_current_user)):
    rows = db.execute(text(
        "SELECT id, document_id, chunk_index, content, token_count "
        "FROM document_chunks WHERE document_id=:id ORDER BY chunk_index"
    ), {"id": doc_id}).mappings().all()
    return [dict(r) for r in rows]


def _get(db: Connection, did: int) -> dict:
    row = db.execute(text(
        "SELECT id, topic_id, uploader_id, title, source_type, content, "
        "chunks_count, status, uploaded_at FROM documents WHERE id=:id"
    ), {"id": did}).mappings().first()
    if not row:
        raise HTTPException(404, "document not found")
    return dict(row)
