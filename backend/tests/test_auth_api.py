import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.engine import Engine
from app.main import app
from app.db import get_db


@pytest.fixture(autouse=True)
def override_db(db_engine: Engine):
    """Wire FastAPI's get_db dependency to the test engine."""
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


@pytest.mark.asyncio
async def test_register_then_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/auth/register", json={
            "username": "testuser", "email": "t@t.com", "password": "secret123"
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

        r2 = await ac.post("/api/auth/login",
                           json={"username": "testuser", "password": "secret123"})
        assert r2.status_code == 200
        token = r2.json()["access_token"]

        r3 = await ac.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r3.status_code == 200
        assert r3.json()["username"] == "testuser"
