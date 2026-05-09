from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import settings

# Pool sizing: small servers (2GB) → keep ~3 idle conns. Each MySQL
# connection costs ~2-4MB on the DB side and a small struct on the
# Python side. A pool of 3+2 fits a 2C2G box comfortably.
engine: Engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
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
