from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.finding import Finding
from ..models.user import User
from ..security.auth import get_current_active_user
from ..services.audit_service import log_audit
from ..analytics.anomaly import anomaly_detector
from ..graph.graph_service import graph_service
import json

router = APIRouter(prefix="/api/findings", tags=["findings"])

@router.get("")
def list_findings(case_id: int = None, status: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    query = db.query(Finding)
    if case_id:
        query = query.filter(Finding.case_id == case_id)
    if status:
        query = query.filter(Finding.status == status)
    
    findings = query.order_by(Finding.created_at.desc()).limit(100).all()
    return findings

@router.get("/anomalies")
def get_anomalies(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    graph_data = graph_service.get_graph_data(limit=500)
    anomalies = anomaly_detector.detect_all(db, graph_data)
    
    # Optionally save to findings table if not exists
    for anomaly in anomalies[:5]:
        existing = db.query(Finding).filter(Finding.title == anomaly["title"]).first()
        if not existing:
            finding = Finding(
                finding_type=anomaly["finding_type"],
                title=anomaly["title"],
                description=anomaly["description"],
                severity=anomaly["severity"],
                confidence=anomaly["confidence"],
                status="NEW",
                evidence=json.dumps(anomaly.get("evidence", {})),
                entities_involved=json.dumps(anomaly.get("entities_involved", []))
            )
            db.add(finding)
    db.commit()
    
    return {"anomalies": anomalies, "total": len(anomalies)}

@router.post("/{finding_id}/review")
def review_finding(finding_id: int, action: str, notes: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    if action == "dismiss":
        finding.status = "FALSE_POSITIVE"
    elif action == "save":
        finding.status = "SAVED"
    elif action == "reviewed":
        finding.status = "REVIEWED"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    
    log_audit(db, current_user.id, current_user.username, f"FINDING_{action.upper()}", "FINDING", finding_id, f"{action} finding {finding.title}")
    
    return {"message": f"Finding marked as {finding.status}", "finding": finding}

@router.post("/generate")
def generate_findings(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    graph_data = graph_service.get_graph_data(limit=500)
    anomalies = anomaly_detector.detect_all(db, graph_data)
    
    created = 0
    for anomaly in anomalies:
        existing = db.query(Finding).filter(Finding.title == anomaly["title"]).first()
        if not existing:
            finding = Finding(
                finding_type=anomaly["finding_type"],
                title=anomaly["title"],
                description=anomaly["description"],
                severity=anomaly["severity"],
                confidence=anomaly["confidence"],
                status="NEW",
                evidence=json.dumps(anomaly.get("evidence", {})),
                entities_involved=json.dumps(anomaly.get("entities_involved", []))
            )
            db.add(finding)
            created += 1
    db.commit()
    
    log_audit(db, current_user.id, current_user.username, "FINDINGS_GENERATED", "FINDING", None, f"Generated {created} new findings")
    
    return {"message": f"Generated {created} new findings", "total_anomalies": len(anomalies)}
