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
