-- ============================================================
-- Performance experiments
-- For each pair: drop index -> EXPLAIN ANALYZE -> recreate -> EXPLAIN ANALYZE.
-- ============================================================

-- Experiment 1: idx_relationships_src_dst_type (lookup by src+dst)
ALTER TABLE relationships DROP INDEX idx_relationships_src_dst_type;
EXPLAIN ANALYZE
  SELECT * FROM relationships WHERE source_entity_id=500 AND target_entity_id=1500;
CREATE INDEX idx_relationships_src_dst_type
  ON relationships(source_entity_id, target_entity_id, relation_type);
EXPLAIN ANALYZE
  SELECT * FROM relationships WHERE source_entity_id=500 AND target_entity_id=1500;

-- Experiment 2: idx_mapping_entity (reverse lookup)
ALTER TABLE chunk_entity_mapping DROP INDEX idx_mapping_entity;
EXPLAIN ANALYZE
  SELECT chunk_id FROM chunk_entity_mapping WHERE entity_id = 1234;
CREATE INDEX idx_mapping_entity ON chunk_entity_mapping(entity_id);
EXPLAIN ANALYZE
  SELECT chunk_id FROM chunk_entity_mapping WHERE entity_id = 1234;

-- Experiment 3: FULLTEXT vs LIKE
EXPLAIN ANALYZE
  SELECT id FROM document_chunks WHERE content LIKE '%keyword-7%';
EXPLAIN ANALYZE
  SELECT id FROM document_chunks WHERE MATCH(content) AGAINST('keyword-7' IN NATURAL LANGUAGE MODE);

-- Experiment 4: leftmost prefix demo
EXPLAIN
  SELECT * FROM entities WHERE entity_type='person';
EXPLAIN
  SELECT * FROM entities WHERE topic_id=1 AND entity_type='person';
