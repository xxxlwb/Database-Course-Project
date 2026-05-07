import pytest
from app.services.sql_console import execute_one, validate


def test_validate_rejects_multi():
    with pytest.raises(ValueError):
        validate("SELECT 1; SELECT 2")


def test_select(db_engine):
    out = execute_one(db_engine, "SELECT 1 AS x")
    assert out["kind"] == "read"
    assert out["rows"] == [[1]]


def test_show_tables(db_engine):
    out = execute_one(db_engine, "SHOW TABLES")
    assert out["row_count"] >= 14
