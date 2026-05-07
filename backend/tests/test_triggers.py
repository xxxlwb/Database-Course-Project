from sqlalchemy import text


def _seed_user_topic(c, uid=1, tid=1):
    c.execute(text("INSERT INTO users (id, username, password_hash, email) "
                   "VALUES (:u, 'u1', 'x', 'u1@u.com')"), {"u": uid})
    c.execute(text("INSERT INTO topics (id, name, owner_id) "
                   "VALUES (:t, 't1', :u)"), {"t": tid, "u": uid})


def test_trigger_documents_after_insert(db_engine):
    with db_engine.connect() as c:
        _seed_user_topic(c)
        c.execute(text(
            "INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
            "VALUES (1, 1, 1, 'Doc1', 'text', REPEAT('a', 64))"
        ))
        c.commit()

        doc_count = c.execute(text("SELECT doc_count FROM topics WHERE id=1")).scalar()
        assert doc_count == 1, f"expected doc_count=1, got {doc_count}"

        job_count = c.execute(text(
            "SELECT COUNT(*) FROM extraction_jobs WHERE document_id=1 AND job_type='cognitive_map'"
        )).scalar()
        assert job_count == 1

        audit_count = c.execute(text(
            "SELECT COUNT(*) FROM audit_logs WHERE entity_type='document' AND entity_id=1 AND action='create'"
        )).scalar()
        assert audit_count == 1


def test_trigger_chunks_after_insert(db_engine):
    with db_engine.connect() as c:
        _seed_user_topic(c)
        c.execute(text(
            "INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
            "VALUES (1, 1, 1, 'Doc', 'text', REPEAT('b', 64))"
        ))
        c.commit()

        c.execute(text(
            "INSERT INTO document_chunks (document_id, chunk_index, content) "
            "VALUES (1, 0, 'chunk0'), (1, 1, 'chunk1')"
        ))
        c.commit()

        cnt = c.execute(text("SELECT chunks_count FROM documents WHERE id=1")).scalar()
        assert cnt == 2, f"expected 2 chunks counted, got {cnt}"

        status = c.execute(text("SELECT status FROM documents WHERE id=1")).scalar()
        assert status == "chunking", f"expected status 'chunking', got {status}"


def test_trigger_relationships_blocks_cross_topic(db_engine):
    with db_engine.connect() as c:
        c.execute(text("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')"))
        c.execute(text("INSERT INTO topics (id, name, owner_id) VALUES (1,'A',1),(2,'B',1)"))
        c.execute(text(
            "INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
            "VALUES (1,1,'X','person'),(2,2,'Y','person')"
        ))
        c.commit()
        try:
            c.execute(text(
                "INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type) "
                "VALUES (1, 1, 2, 'knows')"
            ))
            c.commit()
            assert False, "expected cross-topic to be rejected"
        except Exception as e:
            assert "cross-topic" in str(e) or "45000" in str(e)


def test_trigger_entities_rename_marks_blueprint_outdated(db_engine):
    with db_engine.connect() as c:
        _seed_user_topic(c)
        c.execute(text(
            "INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
            "VALUES (1, 1, 'old', 'person')"
        ))
        c.execute(text(
            "INSERT INTO analysis_blueprints (topic_id, status) VALUES (1, 'ready')"
        ))
        c.execute(text("UPDATE topics SET blueprint_status='ready' WHERE id=1"))
        c.commit()

        c.execute(text("UPDATE entities SET canonical_name='new' WHERE id=1"))
        c.commit()

        bs = c.execute(text("SELECT blueprint_status FROM topics WHERE id=1")).scalar()
        assert bs == "outdated"

        audit = c.execute(text(
            "SELECT COUNT(*) FROM audit_logs WHERE action='rename' AND entity_id=1"
        )).scalar()
        assert audit == 1


def test_trigger_chunk_entity_increments_mention(db_engine):
    with db_engine.connect() as c:
        _seed_user_topic(c)
        c.execute(text(
            "INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
            "VALUES (1,1,1,'D','text',REPEAT('c',64))"
        ))
        c.execute(text(
            "INSERT INTO document_chunks (id, document_id, chunk_index, content) "
            "VALUES (1,1,0,'x')"
        ))
        c.execute(text(
            "INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
            "VALUES (1,1,'E','concept')"
        ))
        c.commit()

        c.execute(text(
            "INSERT INTO chunk_entity_mapping (chunk_id, entity_id, occurrences) "
            "VALUES (1, 1, 3)"
        ))
        c.commit()

        m = c.execute(text("SELECT mention_count FROM entities WHERE id=1")).scalar()
        assert m == 3
