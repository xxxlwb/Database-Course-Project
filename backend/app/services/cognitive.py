# backend/app/services/cognitive.py
import json
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..llm import gen_cognitive_map


def generate_for_document(db: Connection, doc_id: int) -> dict:
    row = db.execute(text("SELECT content FROM documents WHERE id=:id"),
                     {"id": doc_id}).first()
    if not row or not row[0]:
        raise ValueError("document not found or empty")

    cog = gen_cognitive_map(row[0])

    # upsert
    existing = db.execute(text(
        "SELECT id, version FROM cognitive_maps WHERE document_id=:id"
    ), {"id": doc_id}).first()

    if existing:
        db.execute(text(
            "UPDATE cognitive_maps SET summary=:s, key_entities=:k, themes=:t, "
            "timeline=:tl, structural_patterns=:sp, version=version+1, "
            "generated_by='llm' WHERE id=:cid"
        ), {"s": cog.get("summary"),
            "k": json.dumps(cog.get("key_entities", []), ensure_ascii=False),
            "t": json.dumps(cog.get("themes", []), ensure_ascii=False),
            "tl": json.dumps(cog.get("timeline", []), ensure_ascii=False),
            "sp": json.dumps(cog.get("structural_patterns", []), ensure_ascii=False),
            "cid": existing[0]})
    else:
        db.execute(text(
            "INSERT INTO cognitive_maps (document_id, summary, key_entities, themes, "
            "timeline, structural_patterns, generated_by) "
            "VALUES (:d, :s, :k, :t, :tl, :sp, 'llm')"
        ), {"d": doc_id,
            "s": cog.get("summary"),
            "k": json.dumps(cog.get("key_entities", []), ensure_ascii=False),
            "t": json.dumps(cog.get("themes", []), ensure_ascii=False),
            "tl": json.dumps(cog.get("timeline", []), ensure_ascii=False),
            "sp": json.dumps(cog.get("structural_patterns", []), ensure_ascii=False)})

    return cog
