from sqlalchemy import text


def test_sp_create_extraction_job(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    cur.execute("INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
                "VALUES (1,1,1,'D','text',REPEAT('a',64))")
    raw.commit()

    cur.execute("CALL sp_create_extraction_job(1, 'graph', 1, @jid)")
    cur.execute("SELECT @jid")
    job_id = cur.fetchone()[0]
    assert job_id is not None and job_id > 0

    # Idempotency: calling again with same args returns same id
    cur.execute("CALL sp_create_extraction_job(1, 'graph', 1, @jid2)")
    cur.execute("SELECT @jid2")
    job_id_2 = cur.fetchone()[0]
    assert job_id_2 == job_id

    raw.close()


def test_sp_merge_entities(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    cur.execute("INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
                "VALUES (1,1,'A','person'), (2,1,'B','person'), (3,1,'C','person')")
    cur.execute("INSERT INTO entity_aliases (entity_id, alias) VALUES (2, 'B-alias')")
    cur.execute("INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type) "
                "VALUES (1, 2, 3, 'knows'), (1, 1, 2, 'colleague')")
    raw.commit()

    cur.execute("CALL sp_merge_entities(1, 2, 1)")
    raw.commit()

    cur.execute("SELECT COUNT(*) FROM entities WHERE id=2")
    assert cur.fetchone()[0] == 0, "entity 2 should be deleted"

    cur.execute("SELECT COUNT(*) FROM entity_aliases WHERE entity_id=1 AND alias IN ('B','B-alias')")
    assert cur.fetchone()[0] == 2, "aliases should be migrated"

    cur.execute("SELECT COUNT(*) FROM relationships WHERE source_entity_id=1 AND target_entity_id=3")
    assert cur.fetchone()[0] == 1, "relationship should be redirected"

    cur.execute("SELECT blueprint_status FROM topics WHERE id=1")
    assert cur.fetchone()[0] == 'outdated'

    cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action='merge'")
    assert cur.fetchone()[0] == 1
    raw.close()
