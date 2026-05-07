from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/api/topics", tags=["graph"])


@router.get("/{topic_id}/graph")
def get_graph(topic_id: int,
              limit: int = Query(500, le=2000),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    nodes = db.execute(text(
        "SELECT id, canonical_name, entity_type, mention_count "
        "FROM entities WHERE topic_id=:t ORDER BY mention_count DESC LIMIT :lim"
    ), {"t": topic_id, "lim": limit}).mappings().all()

    node_ids = {n["id"] for n in nodes}
    if not node_ids:
        return {"nodes": [], "edges": []}

    edges = db.execute(text(
        "SELECT id, source_entity_id, target_entity_id, relation_type, weight "
        "FROM relationships WHERE topic_id=:t LIMIT :lim"
    ), {"t": topic_id, "lim": limit}).mappings().all()

    return {
        "nodes": [{"id": n["id"], "name": n["canonical_name"],
                   "type": n["entity_type"], "value": n["mention_count"]}
                  for n in nodes],
        "edges": [{"id": e["id"], "source": e["source_entity_id"],
                   "target": e["target_entity_id"], "label": e["relation_type"],
                   "weight": float(e["weight"])} for e in edges
                  if e["source_entity_id"] in node_ids and e["target_entity_id"] in node_ids],
    }
