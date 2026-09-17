from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.user import User
from ..security.auth import get_current_active_user
from ..graph.graph_service import graph_service
from ..services.audit_service import log_audit

router = APIRouter(prefix="/api/graph", tags=["graph"])

@router.get("")
def get_graph(
    limit: int = Query(300, ge=10, le=1000),
    node_type: Optional[str] = None,
    relationship_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    filters = {}
    if node_type:
        filters["node_type"] = node_type
    if relationship_type:
        filters["relationship_type"] = relationship_type
    
    graph_data = graph_service.get_graph_data(filters=filters, limit=limit)
    
    log_audit(db, current_user.id, current_user.username, "GRAPH_VIEWED", "GRAPH", None, f"Viewed graph with {len(graph_data['nodes'])} nodes")
    
    return graph_data

@router.get("/path")
def get_path(
    source: str,
    target: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = graph_service.find_path(source, target)
    
    log_audit(db, current_user.id, current_user.username, "PATH_SEARCH", "GRAPH", None, f"Searched path from {source} to {target}")
    
    return result

@router.post("/rebuild")
def rebuild_graph(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_val not in ["ADMIN", "INVESTIGATOR"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = graph_service.build_full_graph(db)
    
    log_audit(db, current_user.id, current_user.username, "GRAPH_REBUILT", "GRAPH", None, "Rebuilt graph from database")
    
    return {"status": "success" if success else "failed", "message": "Graph rebuilt from database"}

@router.get("/neighbors/{node_id}")
def get_neighbors(node_id: str, depth: int = 1, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # For memory graph, we need to filter
    graph_data = graph_service.get_graph_data(limit=1000)
    
    # Find neighbors up to depth
    from collections import deque
    
    visited = set([node_id])
    queue = deque([(node_id, 0)])
    neighbor_ids = set([node_id])
    relevant_edges = []
    
    # Build adjacency
    adj = {}
    for edge in graph_data["edges"]:
        adj.setdefault(edge["source"], []).append(edge["target"])
        adj.setdefault(edge["target"], []).append(edge["source"])
    
    while queue:
        current, d = queue.popleft()
        if d >= depth:
            continue
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                neighbor_ids.add(neighbor)
                queue.append((neighbor, d+1))
    
    nodes = [n for n in graph_data["nodes"] if n["id"] in neighbor_ids]
    edges = [e for e in graph_data["edges"] if e["source"] in neighbor_ids and e["target"] in neighbor_ids]
    
    return {"nodes": nodes, "edges": edges, "stats": {"node_count": len(nodes), "edge_count": len(edges)}}
