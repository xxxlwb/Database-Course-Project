-- Secondary indexes for performance
CREATE INDEX idx_documents_topic_status ON documents(topic_id, status);
CREATE INDEX idx_documents_content_hash ON documents(content_hash);
CREATE INDEX idx_entities_topic_type_name ON entities(topic_id, entity_type, canonical_name);
CREATE INDEX idx_relationships_src_dst_type ON relationships(source_entity_id, target_entity_id, relation_type);
CREATE INDEX idx_mapping_entity ON chunk_entity_mapping(entity_id);
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, created_at);
CREATE FULLTEXT INDEX ft_chunks_content ON document_chunks(content);

-- RAG-reserved indexes (model filter)
CREATE INDEX idx_chunk_emb_model ON chunk_embeddings(model);
CREATE INDEX idx_entity_emb_model ON entity_embeddings(model);
