import os
import pytest
from sqlalchemy import create_engine, text

# Tests use a separate database: nkg_test
TEST_DB = "nkg_test"

def _admin_url():
    user = os.getenv("DB_USER", "root")
    pwd = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}"

def _test_url():
    return f"{_admin_url()}/{TEST_DB}?charset=utf8mb4"

@pytest.fixture(scope="session")
def db_engine():
    """Create test database, run schema, yield engine, drop database."""
    admin = create_engine(_admin_url(), isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB}"))
        c.execute(text(f"CREATE DATABASE {TEST_DB} DEFAULT CHARSET utf8mb4"))

    engine = create_engine(_test_url(), pool_pre_ping=True)

    # Apply all SQL files in order
    sql_dir = os.path.join(os.path.dirname(__file__), "..", "..", "sql")
    for fname in ["01_schema.sql", "02_indexes.sql", "03_views.sql",
                  "04_triggers.sql", "05_procedures.sql"]:
        path = os.path.join(sql_dir, fname)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            sql_text = f.read()
        # MySQL multi-statement: split by DELIMITER blocks
        _exec_sql_file(engine, sql_text)

    yield engine

    engine.dispose()
    with admin.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB}"))
    admin.dispose()


def _exec_sql_file(engine, sql_text):
    """Naive splitter that respects DELIMITER directives."""
    delim = ";"
    buf = []
    statements = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("DELIMITER"):
            if buf:
                statements.append("\n".join(buf).strip())
                buf = []
            delim = stripped.split(None, 1)[1]
            continue
        if stripped.endswith(delim):
            buf.append(line[: line.rfind(delim)])
            statements.append("\n".join(buf).strip())
            buf = []
        else:
            buf.append(line)
    if buf:
        rest = "\n".join(buf).strip()
        if rest:
            statements.append(rest)

    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        for stmt in statements:
            if stmt and not stmt.startswith("--"):
                cur.execute(stmt)
        raw.commit()
    finally:
        raw.close()


@pytest.fixture(autouse=True)
def db_clean(db_engine):
    """Truncate every data table before each test (preserve schema/triggers/SPs)."""
    tables = [
        "audit_logs", "extraction_jobs", "chunk_entity_mapping",
        "relationships", "entity_aliases", "entities",
        "analysis_blueprints", "cognitive_maps", "document_chunks",
        "documents", "topics", "users",
        "chunk_embeddings", "entity_embeddings",
    ]
    with db_engine.connect() as c:
        c.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in tables:
            c.execute(text(f"TRUNCATE TABLE {t}"))
        c.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        c.commit()
    yield
