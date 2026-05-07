import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.engine import Engine
from app.main import app
from app.db import get_db
from app.routers import entities as entities_router


@pytest.fixture(autouse=True)
def override_db(db_engine: Engine, monkeypatch):
    """Wire FastAPI's get_db dep AND the module-level engine (used for SP calls)
    to the test engine, so that endpoints touching SPs hit nkg_test."""
    def _get_test_db():
        conn = db_engine.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    app.dependency_overrides[get_db] = _get_test_db
    monkeypatch.setattr(entities_router, "engine", db_engine)
    yield
    app.dependency_overrides.pop(get_db, None)


async def _bootstrap(ac):
    await ac.post("/api/auth/register", json={
        "username": "ent1", "email": "e@e.com", "password": "secret123"})
    r = await ac.post("/api/auth/login", json={"username": "ent1", "password": "secret123"})
    tok = r.json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    r = await ac.post("/api/topics", json={"name": "T"}, headers=h)
    return h, r.json()["id"]


@pytest.mark.asyncio
async def test_entity_crud_and_merge(db_engine):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        h, tid = await _bootstrap(ac)

        r1 = await ac.post("/api/entities", json={
            "topic_id": tid, "canonical_name": "X", "entity_type": "person"}, headers=h)
        r2 = await ac.post("/api/entities", json={
            "topic_id": tid, "canonical_name": "Y", "entity_type": "person"}, headers=h)
        e1, e2 = r1.json()["id"], r2.json()["id"]

        r = await ac.post("/api/entities/merge",
                          json={"keep_id": e1, "merge_id": e2}, headers=h)
        assert r.status_code == 200

        r = await ac.get(f"/api/entities/{e2}", headers=h)
        assert r.status_code == 404
