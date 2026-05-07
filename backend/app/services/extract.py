# backend/app/services/extract.py
import json
from typing import Optional
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..llm import gen_extraction


def extract_for_topic(db: Connection, topic_id: int, doc_id: Optional[int] = None) -> dict:
    """Run LLM extraction on chunks; INSERT IGNORE entities/rels/mappings."""
    sql = ("SELECT dc.id, dc.content FROM document_chunks dc "
           "JOIN documents d ON d.id = dc.document_id WHERE d.topic_id=:t")
    p = {"t": topic_id}
    if doc_id:
        sql += " AND d.id=:d"; p["d"] = doc_id

    chunks = db.execute(text(sql), p).all()
    if not chunks:
        raise ValueError("no chunks for topic")

    known = [r[0] for r in db.execute(text(
        "SELECT canonical_name FROM entities WHERE topic_id=:t LIMIT 200"
    ), {"t": topic_id}).all()]

    new_ent = 0; new_rel = 0; new_map = 0
    for chunk_id, content in chunks:
        result = gen_extraction(content, known)
        for e in result.get("entities", []):
            name, etype = e.get("name"), e.get("type", "other")
            if not name:
                continue
            try:
                db.execute(text(
                    "INSERT IGNORE INTO entities (topic_id, canonical_name, entity_type) "
                    "VALUES (:t, :n, :ty)"), {"t": topic_id, "n": name, "ty": etype})
                eid = db.execute(text(
                    "SELECT id FROM entities WHERE topic_id=:t AND canonical_name=:n AND entity_type=:ty"
                ), {"t": topic_id, "n": name, "ty": etype}).scalar()
                if eid:
                    res = db.execute(text(
                        "INSERT IGNORE INTO chunk_entity_mapping (chunk_id, entity_id, occurrences) "
                        "VALUES (:c, :e, 1)"), {"c": chunk_id, "e": eid})
                    if res.rowcount > 0:
                        new_map += 1
                    new_ent += 1
            except Exception:
                pass

        for r in result.get("relationships", []):
            src, dst, rtype = r.get("source"), r.get("target"), r.get("type")
            if not (src and dst and rtype):
                continue
            sid = db.execute(text(
                "SELECT id FROM entities WHERE topic_id=:t AND canonical_name=:n LIMIT 1"
            ), {"t": topic_id, "n": src}).scalar()
            tid = db.execute(text(
                "SELECT id FROM entities WHERE topic_id=:t AND canonical_name=:n LIMIT 1"
            ), {"t": topic_id, "n": dst}).scalar()
            if sid and tid and sid != tid:
                try:
                    db.execute(text(
                        "INSERT IGNORE INTO relationships (topic_id, source_entity_id, "
                        "target_entity_id, relation_type, description) "
                        "VALUES (:t, :s, :d, :rt, :desc)"
                    ), {"t": topic_id, "s": sid, "d": tid, "rt": rtype,
                        "desc": r.get("description")})
                    new_rel += 1
                except Exception:
                    pass

    return {"new_entities": new_ent, "new_relationships": new_rel, "new_mappings": new_map}
