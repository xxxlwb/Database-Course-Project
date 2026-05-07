from sqlalchemy import text

def test_all_tables_exist(db_engine):
    expected = {
        "users", "topics", "documents", "document_chunks",
        "cognitive_maps", "analysis_blueprints",
        "entities", "entity_aliases", "relationships",
        "chunk_entity_mapping", "extraction_jobs", "audit_logs",
        "chunk_embeddings", "entity_embeddings",
    }
    with db_engine.connect() as c:
        rows = c.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = DATABASE()"
        )).all()
    actual = {r[0] for r in rows}
    missing = expected - actual
    assert not missing, f"Missing tables: {missing}"


def test_users_unique_username(db_engine):
    with db_engine.connect() as c:
        c.execute(text(
            "INSERT INTO users (username, password_hash, email) "
            "VALUES ('alice', 'x', 'a@b.com')"
        ))
        c.commit()
        try:
            c.execute(text(
                "INSERT INTO users (username, password_hash, email) "
                "VALUES ('alice', 'y', 'c@d.com')"
            ))
            c.commit()
            assert False, "expected duplicate username to fail"
        except Exception as e:
            assert "Duplicate" in str(e) or "1062" in str(e)


def test_relationship_self_loop_blocked(db_engine):
    with db_engine.connect() as c:
        c.execute(text(
            "INSERT INTO users (id, username, password_hash, email) "
            "VALUES (1, 'u', 'x', 'u@u.com')"
        ))
        c.execute(text(
            "INSERT INTO topics (id, name, owner_id) VALUES (1, 't', 1)"
        ))
        c.execute(text(
            "INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
            "VALUES (1, 1, 'X', 'person')"
        ))
        c.commit()
        try:
            c.execute(text(
                "INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type) "
                "VALUES (1, 1, 1, 'self')"
            ))
            c.commit()
            assert False, "expected CHECK constraint to block self-loop"
        except Exception as e:
            assert "chk_rel_self" in str(e) or "3819" in str(e) or "Check" in str(e)
