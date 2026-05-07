-- ============================================================
-- NKG Triggers (5)
-- ============================================================

DELIMITER $$

-- 1) After document inserted: bump topic doc_count + create cognitive_map job + audit
DROP TRIGGER IF EXISTS trg_documents_after_insert$$
CREATE TRIGGER trg_documents_after_insert
AFTER INSERT ON documents
FOR EACH ROW
BEGIN
    UPDATE topics SET doc_count = doc_count + 1 WHERE id = NEW.topic_id;

    INSERT INTO extraction_jobs (document_id, topic_id, job_type, status, created_by)
    VALUES (NEW.id, NEW.topic_id, 'cognitive_map', 'pending', NEW.uploader_id);

    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, after_value)
    VALUES (NEW.uploader_id, 'create', 'document', NEW.id,
            JSON_OBJECT('title', NEW.title, 'topic_id', NEW.topic_id));
END$$

DELIMITER ;
