-- Demo data for in-class showcase

-- 3 users (admin / editor / viewer); password = "demo123" (bcrypt cost 12)
INSERT INTO users (username, password_hash, email, role) VALUES
('admin',  '$2b$12$ffG9NVW0N429rEcyX1vTeeseg5lpJv.0r8U6Z7WxviZQhZvoNbi1O', 'admin@nkg.local',  'admin'),
('editor', '$2b$12$8BbswRA.LF2C/j0ps4n0/.xbrU3aK8f3gl9.P3IY3b9qslhsavlUm', 'editor@nkg.local', 'editor'),
('viewer', '$2b$12$rAVGa0Wpg3AqX6BT4IdPDOwxn5PGZsE5SFzE49PbhrpmsKxEyTIP2', 'viewer@nkg.local', 'viewer');

-- 2 topics
INSERT INTO topics (name, description, owner_id) VALUES
('三国人物图谱', '基于《三国演义》构建的人物关系图谱', 2),
('项目复盘', '团队季度复盘文档分析', 2);

-- 4 documents (triggers will create cognitive_map jobs and increment doc_count)
INSERT INTO documents (topic_id, uploader_id, title, source_type, content, content_hash) VALUES
(1, 2, '官渡之战', 'text',
 '建安五年，曹操与袁绍战于官渡。袁绍兵众而粮少，曹操奇袭乌巢烧粮，绍军溃。许攸献策，张郃高览降曹。',
 SHA2('官渡之战', 256)),
(1, 2, '赤壁之战', 'text',
 '建安十三年，孙权刘备联军在周瑜统领下于赤壁大破曹操。诸葛亮舌战群儒促成联盟。黄盖诈降，火烧连营。',
 SHA2('赤壁之战', 256)),
(2, 2, '2024 Q4 复盘', 'markdown',
 '# 2024 Q4 复盘\n\n张三负责支付项目，按期上线。李四主导风控重构，因依赖延期推迟两周。王五处理客户投诉。',
 SHA2('2024Q4', 256)),
(2, 2, '2025 Q1 启动', 'markdown',
 '# 2025 Q1\n\n张三转岗到结算项目，李四继续推进风控2.0，王五接手客服系统重写。',
 SHA2('2025Q1', 256));

-- 8 chunks (2 per document; trigger updates documents.chunks_count and status='chunking')
INSERT INTO document_chunks (document_id, chunk_index, content) VALUES
(1, 0, '建安五年，曹操与袁绍战于官渡。'),
(1, 1, '袁绍兵众而粮少，曹操奇袭乌巢烧粮，绍军溃。'),
(2, 0, '建安十三年，孙刘联军于赤壁大破曹操。'),
(2, 1, '诸葛亮舌战群儒促成联盟。'),
(3, 0, '张三负责支付项目，按期上线。'),
(3, 1, '李四主导风控重构，因依赖延期推迟两周。'),
(4, 0, '张三转岗到结算项目，李四继续推进风控2.0。'),
(4, 1, '王五接手客服系统重写。');

-- Entities for topic 1 (三国)
INSERT INTO entities (topic_id, canonical_name, entity_type) VALUES
(1, '曹操', 'person'),(1, '袁绍', 'person'),(1, '刘备', 'person'),
(1, '孙权', 'person'),(1, '诸葛亮', 'person'),(1, '周瑜', 'person'),
(1, '官渡之战', 'event'),(1, '赤壁之战', 'event');

-- Entities for topic 2 (项目复盘)
INSERT INTO entities (topic_id, canonical_name, entity_type) VALUES
(2, '张三', 'person'),(2, '李四', 'person'),(2, '王五', 'person'),
(2, '支付项目', 'project'),(2, '风控重构', 'project'),(2, '结算项目', 'project'),
(2, '客服系统', 'project');

-- Relationships for topic 1 (entity ids 1-8)
INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type, description) VALUES
(1, 1, 2, '战', '曹袁官渡对决'),
(1, 1, 7, '指挥', NULL),
(1, 2, 7, '指挥', NULL),
(1, 3, 4, '联盟', '孙刘联军'),
(1, 5, 6, '协同', '草船借箭'),
(1, 1, 8, '指挥', NULL),
(1, 6, 8, '指挥', NULL);

-- Relationships for topic 2 (entity ids 9-15)
INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type, description) VALUES
(2, 9, 12, '负责', NULL),
(2, 10, 13, '负责', NULL),
(2, 9, 14, '负责', '转岗后'),
(2, 11, 15, '负责', NULL);

-- Some chunk-entity mappings (trigger increments entities.mention_count)
INSERT INTO chunk_entity_mapping (chunk_id, entity_id, occurrences) VALUES
(1, 1, 1), (1, 2, 1), (2, 1, 1), (2, 2, 1),
(3, 3, 1), (3, 4, 1), (3, 5, 1), (3, 6, 1),
(5, 9, 1), (5, 12, 1),
(6, 10, 1), (6, 13, 1),
(7, 9, 1), (7, 14, 1), (7, 10, 1),
(8, 11, 1), (8, 15, 1);
