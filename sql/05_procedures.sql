-- ============================================================
-- NKG Stored Procedures (6)
--   Parametric: sp_create_extraction_job, sp_merge_entities,
--               sp_get_entity_neighborhood
--   Cursor-based: sp_recompute_entity_mentions,
--                 sp_archive_inactive_topics,
--                 sp_propagate_entity_rename
-- ============================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_create_extraction_job$$
CREATE PROCEDURE sp_create_extraction_job(
    IN p_doc_id BIGINT,
    IN p_job_type VARCHAR(32),
    IN p_user_id BIGINT,
    OUT p_job_id BIGINT
)
BEGIN
    DECLARE v_topic_id BIGINT;
    DECLARE v_existing BIGINT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_job_id = NULL;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT topic_id INTO v_topic_id FROM documents WHERE id = p_doc_id;
    IF v_topic_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'document not found';
    END IF;

    SELECT id INTO v_existing
      FROM extraction_jobs
     WHERE document_id = p_doc_id
       AND job_type = p_job_type
       AND status IN ('pending', 'running')
     LIMIT 1;

    IF v_existing > 0 THEN
        SET p_job_id = v_existing;
    ELSE
        INSERT INTO extraction_jobs (document_id, topic_id, job_type, status, created_by)
        VALUES (p_doc_id, v_topic_id, p_job_type, 'pending', p_user_id);
        SET p_job_id = LAST_INSERT_ID();

        INSERT INTO audit_logs (user_id, action, entity_type, entity_id, after_value)
        VALUES (p_user_id, 'create', 'extraction_job', p_job_id,
                JSON_OBJECT('document_id', p_doc_id, 'job_type', p_job_type));
    END IF;

    COMMIT;
END$$

DELIMITER ;
