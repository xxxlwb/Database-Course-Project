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


def test_sp_get_entity_neighborhood(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    # Build chain: 1 - 2 - 3 - 4
    cur.execute("INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
                "VALUES (1,1,'A','person'),(2,1,'B','person'),(3,1,'C','person'),(4,1,'D','person')")
    cur.execute("INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type) "
                "VALUES (1,1,2,'r'),(1,2,3,'r'),(1,3,4,'r')")
    raw.commit()

    cur.execute("CALL sp_get_entity_neighborhood(1, 2, @cnt)")
    rows = cur.fetchall()
    cur.execute("SELECT @cnt")
    cnt = cur.fetchone()[0]
    assert cnt == 3, f"expected nodes (1,2,3) (depth 2 from 1), got cnt={cnt}, rows={rows}"
    raw.close()


def test_sp_recompute_entity_mentions(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    cur.execute("INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
                "VALUES (1,1,1,'D','text',REPEAT('a',64))")
    cur.execute("INSERT INTO document_chunks (id, document_id, chunk_index, content) "
                "VALUES (1,1,0,'a'),(2,1,1,'b')")
    cur.execute("INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
                "VALUES (1,1,'X','concept'),(2,1,'Y','concept')")
    # trigger will set mention_count to 5+3=8 for entity 1 and 7 for entity 2
    cur.execute("INSERT INTO chunk_entity_mapping (chunk_id, entity_id, occurrences) "
                "VALUES (1,1,5),(2,1,3),(1,2,7)")
    # corrupt mention_count manually
    cur.execute("UPDATE entities SET mention_count = 999 WHERE id IN (1,2)")
    raw.commit()

    cur.execute("CALL sp_recompute_entity_mentions()")
    raw.commit()

    cur.execute("SELECT id, mention_count FROM entities ORDER BY id")
    rows = dict(cur.fetchall())
    assert rows[1] == 8, f"entity 1 expected 8, got {rows[1]}"
    assert rows[2] == 7, f"entity 2 expected 7, got {rows[2]}"
    raw.close()
