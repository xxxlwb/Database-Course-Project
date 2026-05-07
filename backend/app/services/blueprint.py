# backend/app/services/blueprint.py
import json
import hashlib
from typing import List
from sqlalchemy import text
from sqlalchemy.engine import Connection


def regenerate_for_topic(db: Connection, topic_id: int) -> dict:
    """Aggregate cognitive maps in topic into a blueprint (no LLM call needed —
    pure aggregation; LLM optional refinement future work)."""
    rows = db.execute(text("""
        SELECT cm.key_entities, cm.themes, cm.timeline
          FROM cognitive_maps cm
          JOIN documents d ON d.id = cm.document_id
         WHERE d.topic_id = :t
    """), {"t": topic_id}).all()

    if not rows:
        raise ValueError("no cognitive maps for topic")

    canonical_entities: dict = {}
    key_patterns = set()
    global_timeline: list = []
    for ke_json, themes_json, tl_json in rows:
        for e in (json.loads(ke_json) if ke_json else []):
            name = e.get("name")
            if name:
                canonical_entities.setdefault(name, {"name": name, "type": e.get("type", "other"), "freq": 0})
                canonical_entities[name]["freq"] += 1
        for t in (json.loads(themes_json) if themes_json else []):
            key_patterns.add(t)
        for ev in (json.loads(tl_json) if tl_json else []):
            global_timeline.append(ev)

    payload = {
        "canonical_entities": list(canonical_entities.values()),
        "key_patterns": sorted(key_patterns),
        "global_timeline": global_timeline,
    }
    sd_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    existing = db.execute(text("SELECT id FROM analysis_blueprints WHERE topic_id=:t"),
                          {"t": topic_id}).first()
    if existing:
        db.execute(text("""
            UPDATE analysis_blueprints
               SET canonical_entities=:ce, key_patterns=:kp, global_timeline=:gt,
                   contributing_doc_count=:dc, source_data_hash=:sh,
                   status='ready', version=version+1, generated_at=NOW()
             WHERE id=:id
        """), {"ce": json.dumps(payload["canonical_entities"], ensure_ascii=False),
               "kp": json.dumps(payload["key_patterns"], ensure_ascii=False),
               "gt": json.dumps(payload["global_timeline"], ensure_ascii=False),
               "dc": len(rows), "sh": sd_hash, "id": existing[0]})
    else:
        db.execute(text("""
            INSERT INTO analysis_blueprints (topic_id, canonical_entities, key_patterns,
                global_timeline, contributing_doc_count, source_data_hash, status, generated_at)
            VALUES (:t, :ce, :kp, :gt, :dc, :sh, 'ready', NOW())
        """), {"t": topic_id,
               "ce": json.dumps(payload["canonical_entities"], ensure_ascii=False),
               "kp": json.dumps(payload["key_patterns"], ensure_ascii=False),
               "gt": json.dumps(payload["global_timeline"], ensure_ascii=False),
               "dc": len(rows), "sh": sd_hash})

    db.execute(text("UPDATE topics SET blueprint_status='ready' WHERE id=:t"),
               {"t": topic_id})

    return payload
