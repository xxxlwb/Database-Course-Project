from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..db import engine
from ..deps import require_role
from ..config import settings

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


# ---------------------------------------------------------------------------
# LLM runtime configuration (in-memory; reverts to .env on restart)
# ---------------------------------------------------------------------------

AVAILABLE_MODELS = [
    "MiniMax-M2",
    "MiniMax-M2.7",
    "MiniMax-M2.7-highspeed",
    "MiniMax-M2.5",
    "MiniMax-M2.5-highspeed",
    "MiniMax-M2.1",
    "MiniMax-M2.1-highspeed",
]


class LLMConfigOut(BaseModel):
    provider: str = "minimax"
    model: str
    base_url: str
    api_key_set: bool
    mock: bool
    available_models: list[str]


class LLMConfigIn(BaseModel):
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    mock: bool | None = None


@router.get("/llm-config", response_model=LLMConfigOut)
def get_llm_config(u=Depends(require_role("admin"))):
    return LLMConfigOut(
        model=settings.minimax_model,
        base_url=settings.minimax_base_url,
        api_key_set=bool(settings.minimax_api_key),
        mock=settings.llm_mock or not settings.minimax_api_key,
        available_models=AVAILABLE_MODELS,
    )


@router.post("/llm-config", response_model=LLMConfigOut)
def set_llm_config(payload: LLMConfigIn, u=Depends(require_role("admin"))):
    if payload.model is not None:
        if payload.model not in AVAILABLE_MODELS:
            raise HTTPException(400, f"unknown model; allowed: {AVAILABLE_MODELS}")
        settings.minimax_model = payload.model
    if payload.base_url is not None:
        settings.minimax_base_url = payload.base_url.strip()
    if payload.api_key is not None:
        # empty string clears the key (forces mock mode)
        settings.minimax_api_key = payload.api_key.strip()
    if payload.mock is not None:
        settings.llm_mock = payload.mock
    return get_llm_config(u)
