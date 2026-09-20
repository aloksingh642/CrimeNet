from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..security.auth import get_current_active_user
from ..graph.graph_service import graph_service
from ..analytics.centrality import analytics_service
from ..analytics.anomaly import anomaly_detector
from ..services.audit_service import log_audit

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/centrality")
def get_centrality(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    graph_data = graph_service.get_graph_data(limit=500)
    result = analytics_service.calculate_centrality(graph_data)
    
    log_audit(db, current_user.id, current_user.username, "ANALYTICS_VIEWED", "ANALYTICS", None, "Viewed centrality analytics")
    
    return result

@router.get("/communities")
def get_communities(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    graph_data = graph_service.get_graph_data(limit=500)
    community_map = analytics_service.detect_communities(graph_data)

    groups = {}

    for node_id, community_id in community_map.items():
        groups.setdefault(community_id, []).append(node_id)

    nodes_by_id = {
        node["id"]: node
        for node in graph_data.get("nodes", [])
    }

    community_list = []

    for community_id, members in groups.items():
        type_distribution = {}

        for node_id in members:
            node_type = nodes_by_id.get(node_id, {}).get("type", "unknown")
            type_distribution[node_type] = type_distribution.get(node_type, 0) + 1

        community_list.append({
            "id": community_id,
            "size": len(members),
            "description": f"Detected community containing {len(members)} connected entities.",
            "type_distribution": type_distribution,
            "central_nodes": members[:5],
        })

    log_audit(
        db,
        current_user.id,
        current_user.username,
        "COMMUNITIES_VIEWED",
        "ANALYTICS",
        None,
        f"Viewed {len(community_list)} communities"
    )

    return {
        "communities": community_list,
        "total": len(community_list)
    }

@router.get("/anomalies")
def get_anomalies(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    graph_data = graph_service.get_graph_data(limit=500)
    anomalies = anomaly_detector.detect_all(db, graph_data)
    
    log_audit(db, current_user.id, current_user.username, "ANOMALIES_VIEWED", "ANALYTICS", None, f"Viewed {len(anomalies)} anomalies")
    
    return {"anomalies": anomalies, "total": len(anomalies)}

@router.get("/overview")
def get_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    from ..models.person import Person
    from ..models.phone import Phone
    from ..models.vehicle import Vehicle
    from ..models.incident import Incident
    from ..models.communication import Communication
    from ..models.financial import Transaction
    from ..models.case import Case
    from ..models.finding import Finding
    
    graph_data = graph_service.get_graph_data(limit=500)
    centrality = analytics_service.calculate_centrality(graph_data)
    communities = analytics_service.detect_communities(graph_data)
    anomalies = anomaly_detector.detect_all(db, graph_data)
    
    stats = {
        "total_entities": len(graph_data["nodes"]),
        "total_relationships": len(graph_data["edges"]),
        "persons": db.query(Person).count(),
        "phones": db.query(Phone).count(),
        "vehicles": db.query(Vehicle).count(),
        "incidents": db.query(Incident).count(),
        "communications": db.query(Communication).count(),
        "transactions": db.query(Transaction).count(),
        "cases": db.query(Case).count(),
        "findings": len(anomalies),
        "communities": len(communities),
        "density": centrality.get("density", 0),
        "components": centrality.get("components", 0)
    }
    
    return {
        "stats": stats,
        "top_central": centrality.get("degree", [])[:5],
        "communities": communities[:3],
        "recent_anomalies": anomalies[:5]
    }
