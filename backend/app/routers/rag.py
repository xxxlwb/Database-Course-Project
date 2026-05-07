from fastapi import APIRouter, HTTPException, Depends
from ..deps import require_role

router = APIRouter(prefix="/api/rag", tags=["rag"])


def _stub():
    raise HTTPException(501, "RAG reserved; not implemented this term")


@router.post("/embed/chunks")
def embed_chunks(u=Depends(require_role("admin"))): _stub()


@router.post("/embed/entities")
def embed_entities(u=Depends(require_role("admin"))): _stub()


@router.post("/search/chunks")
def search_chunks(u=Depends(require_role("admin"))): _stub()


@router.post("/search/entities")
def search_entities(u=Depends(require_role("admin"))): _stub()


@router.post("/answer")
def answer(u=Depends(require_role("admin"))): _stub()
