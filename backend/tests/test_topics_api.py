import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.engine import Engine
from app.main import app
from app.db import get_db


@pytest.fixture(autouse=True)
def override_db(db_engine: Engine):
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
    yield
    app.dependency_overrides.pop(get_db, None)


async def _login(ac):
    await ac.post("/api/auth/register", json={
        "username": "top1", "email": "t1@t.com", "password": "secret123"})
    r = await ac.post("/api/auth/login", json={"username": "top1", "password": "secret123"})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_topic_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        tok = await _login(ac)
        h = {"Authorization": f"Bearer {tok}"}

        r = await ac.post("/api/topics", json={"name": "demo", "description": "d"}, headers=h)
        assert r.status_code == 201
        tid = r.json()["id"]

        r = await ac.get("/api/topics", headers=h)
        assert any(t["id"] == tid for t in r.json())

        r = await ac.patch(f"/api/topics/{tid}", json={"is_archived": True}, headers=h)
        assert r.json()["is_archived"] is True

        r = await ac.delete(f"/api/topics/{tid}", headers=h)
        assert r.status_code == 204
