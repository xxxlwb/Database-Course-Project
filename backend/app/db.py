from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import settings

engine: Engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=5,
    pool_recycle=3600,
)


@contextmanager
def get_conn():
    """Yield a SQLAlchemy Connection (autocommit off, manual commit)."""
    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db():
    """FastAPI dependency."""
    with get_conn() as c:
        yield c
