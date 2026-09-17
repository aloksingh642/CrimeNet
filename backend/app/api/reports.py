from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.case import Case
from ..models.user import User
from ..security.auth import get_current_active_user
from ..graph.graph_service import graph_service
from ..analytics.centrality import analytics_service
from ..analytics.anomaly import anomaly_detector
from ..services.audit_service import log_audit
from datetime import datetime

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/case/{case_id}")
def generate_case_report(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    graph_data = graph_service.get_graph_data(limit=500)
    centrality = analytics_service.calculate_centrality(graph_data)
    communities = analytics_service.detect_communities(graph_data)
    anomalies = anomaly_detector.detect_all(db, graph_data)
    
    report = {
        "case": {
            "case_number": case.case_number,
            "title": case.title,
            "description": case.description,
            "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            "investigator": case.investigator_name,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "priority": case.priority
        },
        "executive_summary": f"Investigation analysis for {case.title} covering {len(graph_data['nodes'])} entities and {len(graph_data['edges'])} relationships. Detected {len(communities)} network communities and {len(anomalies)} patterns requiring review.",
        "network_statistics": {
            "total_entities": len(graph_data["nodes"]),
            "total_relationships": len(graph_data["edges"]),
            "density": centrality.get("density", 0),
            "components": centrality.get("components", 0),
            "communities_detected": len(communities)
        },
        "most_connected": centrality.get("degree", [])[:10],
        "communities": communities[:5],
        "detected_patterns": anomalies[:10],
        "timeline_summary": "Timeline analysis shows activity across multiple event types. See timeline module for detailed chronological view.",
        "evidence_summary": f"Evidence includes {len(graph_data['edges'])} relationships derived from communication records, financial transactions, and incident reports.",
        "disclaimer": "Analytical findings are decision-support outputs and require human verification. This system is an investigator-assistance tool and does NOT automatically declare any person as criminal. All findings must be reviewed by authorized investigators.",
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": current_user.username,
        "classification": "DEMO / SYNTHETIC DATA - FOR TRAINING PURPOSES ONLY"
    }
    
    log_audit(db, current_user.id, current_user.username, "REPORT_GENERATED", "CASE", case_id, f"Generated report for case {case.case_number}")
    
    return report

@router.get("/overview")
def generate_overview_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    from ..models.person import Person
    from ..models.incident import Incident
    
    graph_data = graph_service.get_graph_data(limit=500)
    centrality = analytics_service.calculate_centrality(graph_data)
    communities = analytics_service.detect_communities(graph_data)
    anomalies = anomaly_detector.detect_all(db, graph_data)
    
    report = {
        "title": "CrimeNet Intelligence - System Overview Report",
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": current_user.username,
        "classification": "DEMO / SYNTHETIC DATA",
        "system_stats": {
            "total_entities": len(graph_data["nodes"]),
            "total_relationships": len(graph_data["edges"]),
            "communities": len(communities),
            "anomalies": len(anomalies)
        },
        "network_analysis": centrality,
        "communities": communities,
        "anomalies": anomalies,
        "disclaimer": "Analytical findings are decision-support outputs and require human verification."
    }
    
    return report
