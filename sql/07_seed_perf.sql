-- Performance seed: ~50K chunks, ~10K entities, ~30K relationships, ~50K mappings
-- Run AFTER 06_seed.sql (relies on user 2 / topic 1)

-- Adjust recursion depth for the recursive CTEs below
SET SESSION cte_max_recursion_depth = 100000;

-- 100 documents
INSERT INTO documents (topic_id, uploader_id, title, source_type, content_hash)
WITH RECURSIVE seq AS (
    SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 100
)
SELECT 1, 2, CONCAT('Perf doc ', n), 'text', SHA2(CONCAT('perf', n), 256)
FROM seq;

-- 50K chunks: 500 per doc (only on Perf docs)
-- Materialize Perf doc IDs into a temp table first so the chunks INSERT
-- doesn't read `documents` directly (the AFTER INSERT trigger on
-- document_chunks updates `documents`, which would otherwise raise
-- ERROR 1442 - "table already used by statement which invoked trigger").
DROP TEMPORARY TABLE IF EXISTS _perf_doc_ids;
CREATE TEMPORARY TABLE _perf_doc_ids (id BIGINT PRIMARY KEY);
INSERT INTO _perf_doc_ids SELECT id FROM documents WHERE title LIKE 'Perf doc %';

INSERT INTO document_chunks (document_id, chunk_index, content)
WITH RECURSIVE seq AS (
    SELECT 0 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 499
)
SELECT d.id, s.n, CONCAT('Chunk content ', d.id, '-', s.n,
                          ' lorem ipsum dolor sit amet keyword-', d.id MOD 50)
FROM _perf_doc_ids d
CROSS JOIN seq s
ORDER BY d.id, s.n;

DROP TEMPORARY TABLE _perf_doc_ids;

-- 10K entities (filler in topic 1)
INSERT INTO entities (topic_id, canonical_name, entity_type)
WITH RECURSIVE seq AS (
    SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 10000
)
SELECT 1, CONCAT('PerfEntity-', n),
    ELT(1 + n MOD 8, 'person','project','task','concept','decision','event','place','other')
FROM seq;

-- 30K relationships (random pairs within topic 1, dedup via INSERT IGNORE)
-- Restrict both endpoints to the PerfEntity ID range [16, 10015] so we
-- never pick a topic-2 entity (ids 9-15) and trip the BEFORE INSERT
-- cross-topic guard trigger (which SIGNALs and is NOT suppressed by IGNORE).
INSERT IGNORE INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type)
WITH RECURSIVE seq AS (
    SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 30000
)
SELECT 1,
       16 + FLOOR(RAND(s.n) * 10000),
       16 + FLOOR(RAND(s.n + 1) * 10000),
       ELT(1 + s.n MOD 5, 'related','depends_on','knows','located_in','part_of')
FROM seq s
WHERE 16 + FLOOR(RAND(s.n) * 10000) <> 16 + FLOOR(RAND(s.n + 1) * 10000);

-- 50K chunk-entity mappings
INSERT IGNORE INTO chunk_entity_mapping (chunk_id, entity_id, occurrences)
WITH RECURSIVE seq AS (
    SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 50000
)
SELECT
    1 + FLOOR(RAND(s.n) * 50000),
    9 + FLOOR(RAND(s.n + 1) * 9990),
    1 + s.n MOD 5
FROM seq s;
