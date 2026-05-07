-- ============================================================
-- NKG Schema · MySQL 8.0+ (also works on MySQL 9.x)
-- All tables in 3NF (with documented denormalizations).
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. users
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash CHAR(60) NOT NULL,
    email VARCHAR(128) NOT NULL UNIQUE,
    role ENUM('admin','editor','viewer') NOT NULL DEFAULT 'editor',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户';

-- 2. topics
CREATE TABLE topics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    owner_id BIGINT NOT NULL,
    doc_count INT NOT NULL DEFAULT 0 COMMENT '触发器维护',
    blueprint_status ENUM('outdated','generating','ready','failed') NOT NULL DEFAULT 'outdated',
    is_archived TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_topic_owner_name (owner_id, name),
    CONSTRAINT fk_topics_owner FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主题/语境空间';

-- 3. documents
CREATE TABLE documents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic_id BIGINT NOT NULL,
    uploader_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    source_type ENUM('text','markdown','pdf') NOT NULL DEFAULT 'text',
    original_filename VARCHAR(255),
    file_size BIGINT,
    storage_path VARCHAR(512) COMMENT '大文件落盘路径',
    content MEDIUMTEXT COMMENT '解析后纯文本',
    content_hash CHAR(64) NOT NULL,
    chunks_count INT NOT NULL DEFAULT 0 COMMENT '触发器维护',
    status ENUM('uploaded','chunking','chunk_done','extracting','completed','failed') NOT NULL DEFAULT 'uploaded',
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT fk_documents_uploader FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上传文档';

-- 4. document_chunks
CREATE TABLE document_chunks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    document_id BIGINT NOT NULL,
    chunk_index INT NOT NULL,
    content MEDIUMTEXT NOT NULL,
    content_hash CHAR(64),
    token_count INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_chunk_doc_idx (document_id, chunk_index),
    CONSTRAINT fk_chunks_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档切块';

-- 5. cognitive_maps
CREATE TABLE cognitive_maps (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    document_id BIGINT NOT NULL UNIQUE,
    summary TEXT,
    key_entities JSON,
    themes JSON,
    timeline JSON,
    structural_patterns JSON,
    generated_by VARCHAR(64),
    version INT NOT NULL DEFAULT 1,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_cogmap_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='单文档认知地图';

-- 6. analysis_blueprints
CREATE TABLE analysis_blueprints (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic_id BIGINT NOT NULL UNIQUE,
    canonical_entities JSON,
    key_patterns JSON,
    global_timeline JSON,
    processing_instructions TEXT,
    contributing_doc_count INT,
    source_data_hash CHAR(64),
    status ENUM('outdated','generating','ready','failed') NOT NULL DEFAULT 'outdated',
    version INT NOT NULL DEFAULT 1,
    generated_at DATETIME,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_blueprint_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主题分析蓝图';

-- 7. entities
CREATE TABLE entities (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic_id BIGINT NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    entity_type ENUM('person','project','task','concept','decision','event','place','other') NOT NULL,
    description TEXT,
    attributes JSON,
    mention_count INT NOT NULL DEFAULT 0 COMMENT '触发器维护',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_entity_topic_type_name (topic_id, entity_type, canonical_name),
    CONSTRAINT fk_entities_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实体节点';

-- 8. entity_aliases
CREATE TABLE entity_aliases (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity_id BIGINT NOT NULL,
    alias VARCHAR(255) NOT NULL,
    source ENUM('auto','user') NOT NULL DEFAULT 'auto',
    confidence DECIMAL(3,2) NOT NULL DEFAULT 1.00,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_alias_entity (entity_id, alias),
    CONSTRAINT fk_alias_entity FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实体别名';

-- 9. relationships
CREATE TABLE relationships (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic_id BIGINT NOT NULL,
    source_entity_id BIGINT NOT NULL,
    target_entity_id BIGINT NOT NULL,
    relation_type VARCHAR(64) NOT NULL,
    description TEXT,
    weight DECIMAL(4,3) NOT NULL DEFAULT 1.000,
    attributes JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_rel_topic_src_dst_type (topic_id, source_entity_id, target_entity_id, relation_type),
    CONSTRAINT fk_rel_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT fk_rel_src FOREIGN KEY (source_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    CONSTRAINT fk_rel_dst FOREIGN KEY (target_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    CONSTRAINT chk_rel_self CHECK (source_entity_id <> target_entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实体关系';

-- 10. chunk_entity_mapping
CREATE TABLE chunk_entity_mapping (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    chunk_id BIGINT NOT NULL,
    entity_id BIGINT NOT NULL,
    occurrences INT NOT NULL DEFAULT 1,
    position_info JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_mapping_chunk_entity (chunk_id, entity_id),
    CONSTRAINT fk_mapping_chunk FOREIGN KEY (chunk_id) REFERENCES document_chunks(id) ON DELETE CASCADE,
    CONSTRAINT fk_mapping_entity FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='块-实体映射';

-- 11. extraction_jobs
CREATE TABLE extraction_jobs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    document_id BIGINT,
    topic_id BIGINT NOT NULL,
    job_type ENUM('cognitive_map','blueprint','graph') NOT NULL,
    status ENUM('pending','running','completed','failed') NOT NULL DEFAULT 'pending',
    progress TINYINT NOT NULL DEFAULT 0,
    result JSON,
    error_message TEXT,
    created_by BIGINT,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_user FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='抽取任务状态机';

-- 12. audit_logs
CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(32) NOT NULL,
    entity_type VARCHAR(32),
    entity_id BIGINT,
    before_value JSON,
    after_value JSON,
    ip_address VARCHAR(45),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作审计日志';

-- ============================================================
-- RAG-reserved tables (本期不实现, schema-only forward compat)
-- ============================================================

CREATE TABLE chunk_embeddings (
    chunk_id BIGINT PRIMARY KEY,
    embedding LONGBLOB NOT NULL,
    embedding_dim INT NOT NULL,
    model VARCHAR(64) NOT NULL,
    norm DECIMAL(10,6),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chunk_emb FOREIGN KEY (chunk_id) REFERENCES document_chunks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='RAG 预留: chunk 向量';

CREATE TABLE entity_embeddings (
    entity_id BIGINT PRIMARY KEY,
    embedding LONGBLOB NOT NULL,
    embedding_dim INT NOT NULL,
    model VARCHAR(64) NOT NULL,
    norm DECIMAL(10,6),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_entity_emb FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='RAG 预留: entity 向量';
