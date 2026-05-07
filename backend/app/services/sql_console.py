import re
import time
from typing import Any, Dict, List
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Restrict to single-statement; multi-statement (semicolon-joined) rejected.
# A trailing `;` is allowed (only matches if non-whitespace follows the `;`).
_MULTI_STMT = re.compile(r";\s*\S")


def classify(sql: str) -> str:
    s = sql.strip().upper()
    # Strip a single trailing semicolon for txn-keyword comparison
    s_no_semi = s.rstrip(";").strip()
    if s.startswith("EXPLAIN"):
        return "explain"
    if s.startswith("SELECT") or s.startswith("SHOW") or s.startswith("DESC"):
        return "read"
    if s.startswith(("INSERT", "UPDATE", "DELETE", "REPLACE")):
        return "dml"
    if s.startswith(("CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME")):
        return "ddl"
    if s.startswith("CALL"):
        return "call"
    if s_no_semi in ("BEGIN", "START TRANSACTION", "COMMIT", "ROLLBACK"):
        return "txn"
    return "other"


def validate(sql: str):
    """Raise ValueError on empty or multi-statement SQL."""
    if not sql or not sql.strip():
        raise ValueError("empty SQL")
    if _MULTI_STMT.search(sql):
        raise ValueError("multi-statement SQL not allowed; submit one statement at a time")


def _exec_with_timeout(cur, sql: str):
    """Execute SQL with a 15s read-statement timeout.

    Tries the MariaDB-style ``SET STATEMENT max_statement_time=15 FOR ...``
    prepend first; on syntax error (e.g. running on MySQL which does not
    support that syntax), falls back to setting the MySQL session variable
    ``MAX_EXECUTION_TIME`` (milliseconds) and then running the bare SQL.
    """
    try:
        cur.execute("SET STATEMENT max_statement_time=15 FOR " + sql)
    except Exception:
        # MySQL fallback: session-level optimizer cap (applies to SELECT).
        try:
            cur.execute("SET SESSION MAX_EXECUTION_TIME=15000")
        except Exception:
            pass
        cur.execute(sql)


def execute_one(engine: Engine, sql: str, max_rows: int = 1000) -> Dict[str, Any]:
    """Run single SQL on a fresh raw connection; return structured result."""
    validate(sql)
    kind = classify(sql)
    started = time.perf_counter()
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        # For SELECT/EXPLAIN/SHOW/DESC: enforce 15s timeout
        if kind in ("read", "explain"):
            _exec_with_timeout(cur, sql)
        else:
            cur.execute(sql)

        out: Dict[str, Any] = {"kind": kind, "elapsed_ms": 0}

        if kind in ("read", "explain"):
            cols = [d[0] for d in (cur.description or [])]
            rows = cur.fetchmany(max_rows)
            out["columns"] = cols
            out["rows"] = [list(r) for r in rows]
            out["row_count"] = len(rows)
        elif kind == "call":
            # CALL may return multiple result sets; collect first set's rows + flag extras.
            all_sets: List[List[Any]] = []
            cols = [d[0] for d in (cur.description or [])]
            if cur.description:
                rows = cur.fetchmany(max_rows)
                all_sets.append([list(r) for r in rows])
            # Drain remaining sets
            while cur.nextset():
                if cur.description:
                    extra_rows = cur.fetchmany(max_rows)
                    all_sets.append([list(r) for r in extra_rows])
            raw.commit()
            primary = all_sets[0] if all_sets else []
            out["columns"] = cols
            out["rows"] = primary
            out["row_count"] = len(primary)
            if len(all_sets) > 1:
                out["extra_result_sets"] = len(all_sets) - 1
        elif kind in ("dml", "ddl"):
            raw.commit()
            out["affected_rows"] = cur.rowcount
        elif kind == "txn":
            raw.commit()
        else:
            # "other" — try to expose any result set, else best-effort
            try:
                if cur.description:
                    cols = [d[0] for d in cur.description]
                    rows = cur.fetchmany(max_rows)
                    out["columns"] = cols
                    out["rows"] = [list(r) for r in rows]
                    out["row_count"] = len(rows)
                else:
                    raw.commit()
                    out["affected_rows"] = cur.rowcount
            except Exception:
                raw.commit()

        out["elapsed_ms"] = int((time.perf_counter() - started) * 1000)
        cur.close()
        return out
    except Exception:
        try:
            raw.rollback()
        except Exception:
            pass
        raise
    finally:
        raw.close()
