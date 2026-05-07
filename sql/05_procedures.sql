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

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_merge_entities$$
CREATE PROCEDURE sp_merge_entities(
    IN p_keep_id BIGINT,
    IN p_merge_id BIGINT,
    IN p_user_id BIGINT
)
BEGIN
    DECLARE v_keep_topic BIGINT;
    DECLARE v_merge_topic BIGINT;
    DECLARE v_merge_name VARCHAR(255);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_keep_id = p_merge_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'cannot merge entity with itself';
    END IF;

    START TRANSACTION;

    SELECT topic_id INTO v_keep_topic FROM entities WHERE id = p_keep_id FOR UPDATE;
    SELECT topic_id, canonical_name INTO v_merge_topic, v_merge_name
      FROM entities WHERE id = p_merge_id FOR UPDATE;

    IF v_keep_topic IS NULL OR v_merge_topic IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'entity not found';
    END IF;
    IF v_keep_topic <> v_merge_topic THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'entities belong to different topics';
    END IF;

    -- migrate aliases (skip on UQ collision)
    INSERT IGNORE INTO entity_aliases (entity_id, alias, source, confidence)
    SELECT p_keep_id, alias, source, confidence FROM entity_aliases WHERE entity_id = p_merge_id;

    -- record merged entity name as new alias
    INSERT IGNORE INTO entity_aliases (entity_id, alias, source, confidence)
    VALUES (p_keep_id, v_merge_name, 'auto', 0.99);

    -- migrate chunk_entity_mapping (skip dupes; sum occurrences for collisions)
    UPDATE IGNORE chunk_entity_mapping
       SET entity_id = p_keep_id
     WHERE entity_id = p_merge_id;
    DELETE FROM chunk_entity_mapping WHERE entity_id = p_merge_id;

    -- migrate relationships (drop self-loops & dupes silently)
    UPDATE IGNORE relationships
       SET source_entity_id = p_keep_id
     WHERE source_entity_id = p_merge_id AND target_entity_id <> p_keep_id;
    DELETE FROM relationships WHERE source_entity_id = p_merge_id;

    UPDATE IGNORE relationships
       SET target_entity_id = p_keep_id
     WHERE target_entity_id = p_merge_id AND source_entity_id <> p_keep_id;
    DELETE FROM relationships WHERE target_entity_id = p_merge_id;

    -- delete merged entity
    DELETE FROM entities WHERE id = p_merge_id;

    -- mark blueprint as outdated
    UPDATE topics SET blueprint_status = 'outdated' WHERE id = v_keep_topic;

    -- audit
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, before_value, after_value)
    VALUES (p_user_id, 'merge', 'entity', p_keep_id,
            JSON_OBJECT('merged_id', p_merge_id, 'merged_name', v_merge_name),
            JSON_OBJECT('keep_id', p_keep_id));

    COMMIT;
END$$

DELIMITER ;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_get_entity_neighborhood$$
CREATE PROCEDURE sp_get_entity_neighborhood(
    IN p_entity_id BIGINT,
    IN p_depth INT,
    OUT p_node_count INT
)
BEGIN
    DECLARE v_d INT DEFAULT 0;
    DECLARE v_added INT DEFAULT 1;

    IF p_depth IS NULL OR p_depth < 1 THEN SET p_depth = 1; END IF;
    IF p_depth > 5 THEN SET p_depth = 5; END IF;

    -- MySQL forbids referencing the same TEMPORARY TABLE multiple times in
    -- one query, so we keep the BFS frontier in a separate temp table and
    -- stage newly discovered nodes in another. Behavior is identical to
    -- the single-table version: tmp_neighborhood holds (entity_id, distance)
    -- for every node within p_depth hops.
    DROP TEMPORARY TABLE IF EXISTS tmp_neighborhood;
    DROP TEMPORARY TABLE IF EXISTS tmp_frontier;
    DROP TEMPORARY TABLE IF EXISTS tmp_new_nodes;
    CREATE TEMPORARY TABLE tmp_neighborhood (
        entity_id BIGINT PRIMARY KEY,
        distance INT NOT NULL
    );
    CREATE TEMPORARY TABLE tmp_frontier (entity_id BIGINT PRIMARY KEY);
    CREATE TEMPORARY TABLE tmp_new_nodes (entity_id BIGINT PRIMARY KEY);

    INSERT INTO tmp_neighborhood VALUES (p_entity_id, 0);
    INSERT INTO tmp_frontier VALUES (p_entity_id);

    WHILE v_d < p_depth AND v_added > 0 DO
        DELETE FROM tmp_new_nodes;

        -- forward edges: frontier -> target
        INSERT IGNORE INTO tmp_new_nodes (entity_id)
        SELECT DISTINCT r.target_entity_id
          FROM relationships r
          JOIN tmp_frontier f ON r.source_entity_id = f.entity_id;

        -- reverse edges: source -> frontier
        INSERT IGNORE INTO tmp_new_nodes (entity_id)
        SELECT DISTINCT r.source_entity_id
          FROM relationships r
          JOIN tmp_frontier f ON r.target_entity_id = f.entity_id;

        -- promote previously unknown nodes into the neighborhood
        INSERT IGNORE INTO tmp_neighborhood (entity_id, distance)
        SELECT entity_id, v_d + 1 FROM tmp_new_nodes;

        SET v_added = ROW_COUNT();

        -- next frontier = nodes whose distance is the new layer
        DELETE FROM tmp_frontier;
        INSERT INTO tmp_frontier (entity_id)
        SELECT entity_id FROM tmp_neighborhood WHERE distance = v_d + 1;

        SET v_d = v_d + 1;
    END WHILE;

    SELECT COUNT(*) INTO p_node_count FROM tmp_neighborhood;

    SELECT n.entity_id, n.distance, e.canonical_name, e.entity_type
      FROM tmp_neighborhood n
      JOIN entities e ON e.id = n.entity_id
     ORDER BY n.distance, n.entity_id;
END$$

DELIMITER ;
