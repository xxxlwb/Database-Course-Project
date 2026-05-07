-- v_entity_centrality: degree centrality per entity
CREATE OR REPLACE VIEW v_entity_centrality AS
SELECT
    e.id AS entity_id,
    e.topic_id,
    e.canonical_name,
    e.entity_type,
    e.mention_count,
    COALESCE(out_deg.cnt, 0) AS out_degree,
    COALESCE(in_deg.cnt, 0) AS in_degree,
    COALESCE(out_deg.cnt, 0) + COALESCE(in_deg.cnt, 0) AS total_degree
FROM entities e
LEFT JOIN (
    SELECT source_entity_id AS eid, COUNT(*) AS cnt
    FROM relationships GROUP BY source_entity_id
) out_deg ON e.id = out_deg.eid
LEFT JOIN (
    SELECT target_entity_id AS eid, COUNT(*) AS cnt
    FROM relationships GROUP BY target_entity_id
) in_deg ON e.id = in_deg.eid;

-- v_topic_overview: per-topic stats
CREATE OR REPLACE VIEW v_topic_overview AS
SELECT
    t.id AS topic_id,
    t.name AS topic_name,
    t.owner_id,
    t.is_archived,
    t.blueprint_status,
    t.doc_count,
    COALESCE(ec.entity_cnt, 0) AS entity_count,
    COALESCE(rc.rel_cnt, 0) AS relationship_count,
    t.created_at,
    t.updated_at
FROM topics t
LEFT JOIN (
    SELECT topic_id, COUNT(*) AS entity_cnt FROM entities GROUP BY topic_id
) ec ON t.id = ec.topic_id
LEFT JOIN (
    SELECT topic_id, COUNT(*) AS rel_cnt FROM relationships GROUP BY topic_id
) rc ON t.id = rc.topic_id;

-- v_extraction_job_status: aggregated job overview
CREATE OR REPLACE VIEW v_extraction_job_status AS
SELECT
    j.topic_id,
    t.name AS topic_name,
    j.job_type,
    j.status,
    COUNT(*) AS job_count,
    MAX(j.updated_at) AS last_updated
FROM extraction_jobs j
JOIN topics t ON t.id = j.topic_id
GROUP BY j.topic_id, t.name, j.job_type, j.status;
