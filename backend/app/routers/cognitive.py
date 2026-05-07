# backend/app/routers/cognitive.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..services.cognitive import generate_for_document

router = APIRouter(prefix="/api/documents", tags=["cognitive"])


@router.post("/{doc_id}/cognitive-map")
def gen(doc_id: int, db: Connection = Depends(get_db),
        u: CurrentUser = Depends(get_current_user)):
    try:
        return generate_for_document(db, doc_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/{doc_id}/cognitive-map")
def get(doc_id: int, db: Connection = Depends(get_db),
        u: CurrentUser = Depends(get_current_user)):
    row = db.execute(text(
        "SELECT id, summary, key_entities, themes, timeline, structural_patterns, "
        "version, generated_at FROM cognitive_maps WHERE document_id=:id"
    ), {"id": doc_id}).mappings().first()
    if not row:
        raise HTTPException(404, "no cognitive map")
    return dict(row)
