-- Drop everything in dependency order (children first)
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS extraction_jobs;
DROP TABLE IF EXISTS chunk_entity_mapping;
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS entity_aliases;
DROP TABLE IF EXISTS entities;
DROP TABLE IF EXISTS analysis_blueprints;
DROP TABLE IF EXISTS cognitive_maps;
DROP TABLE IF EXISTS chunk_embeddings;
DROP TABLE IF EXISTS entity_embeddings;
DROP TABLE IF EXISTS document_chunks;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS users;

DROP VIEW IF EXISTS v_entity_centrality;
DROP VIEW IF EXISTS v_topic_overview;
DROP VIEW IF EXISTS v_extraction_job_status;

DROP PROCEDURE IF EXISTS sp_create_extraction_job;
DROP PROCEDURE IF EXISTS sp_merge_entities;
DROP PROCEDURE IF EXISTS sp_get_entity_neighborhood;
DROP PROCEDURE IF EXISTS sp_recompute_entity_mentions;
DROP PROCEDURE IF EXISTS sp_archive_inactive_topics;
DROP PROCEDURE IF EXISTS sp_propagate_entity_rename;

SET FOREIGN_KEY_CHECKS = 1;
