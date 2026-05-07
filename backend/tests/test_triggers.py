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
