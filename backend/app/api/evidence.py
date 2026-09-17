from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.evidence import Evidence, Document
from ..models.communication import Communication
from ..models.financial import Transaction
from ..models.incident import Incident
from ..models.user import User
from ..security.auth import get_current_active_user
from ..services.audit_service import log_audit

router = APIRouter(prefix="/api/evidence", tags=["evidence"])

@router.get("")
def list_evidence(case_id: int = None, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    query = db.query(Evidence)
    if case_id:
        query = query.filter(Evidence.case_id == case_id)
    evidences = query.order_by(Evidence.timestamp.desc()).limit(limit).all()
    
    return [{"id": e.id, "evidence_type": e.evidence_type, "source": e.source, "title": e.title, "content": e.content[:500] if e.content else "", "timestamp": e.timestamp} for e in evidences]

@router.get("/{evidence_id}")
def get_evidence(evidence_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence

@router.get("/relationship/{source}/{target}")
def get_relationship_evidence(source: str, target: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get evidence supporting relationship between two entities"""
    # Search communications, transactions, incidents that mention both
    evidences = []
    
    # Communications
    comms = db.query(Communication).filter(
        ((Communication.source_phone.ilike(f"%{source}%")) | (Communication.destination_phone.ilike(f"%{source}%"))) |
        ((Communication.source_phone.ilike(f"%{target}%")) | (Communication.destination_phone.ilike(f"%{target}%")))
    ).limit(10).all()
    
    for comm in comms:
        evidences.append({
            "type": "COMMUNICATION",
            "id": comm.id,
            "title": f"Communication: {comm.source_phone} → {comm.destination_phone}",
            "content": f"Duration: {comm.duration_seconds}s, Type: {comm.communication_type}, Time: {comm.timestamp}",
            "timestamp": comm.timestamp,
            "confidence": "HIGH"
        })
    
    # Transactions
    txns = db.query(Transaction).filter(
        (Transaction.sender_account.ilike(f"%{source}%")) | (Transaction.receiver_account.ilike(f"%{source}%")) |
        (Transaction.sender_account.ilike(f"%{target}%")) | (Transaction.receiver_account.ilike(f"%{target}%"))
    ).limit(10).all()
    
    for txn in txns:
        evidences.append({
            "type": "TRANSACTION",
            "id": txn.id,
            "title": f"Transaction: ₹{txn.amount}",
            "content": f"From {txn.sender_account} to {txn.receiver_account} at {txn.timestamp}",
            "timestamp": txn.timestamp,
            "confidence": "HIGH"
        })
    
    # Incidents
    incidents = db.query(Incident).filter(
        (Incident.description.ilike(f"%{source}%")) | (Incident.description.ilike(f"%{target}%"))
    ).limit(10).all()
    
    for inc in incidents:
        evidences.append({
            "type": "INCIDENT",
            "id": inc.id,
            "title": f"Incident: {inc.incident_number}",
            "content": inc.description,
            "timestamp": inc.date,
            "confidence": "MEDIUM"
        })
    
    log_audit(db, current_user.id, current_user.username, "EVIDENCE_VIEWED", "EVIDENCE", None, f"Viewed evidence for relationship {source} -> {target}")
    
    return {"source": source, "target": target, "evidences": evidences, "total": len(evidences)}

@router.get("/entity/{entity_id}")
def get_entity_evidence(entity_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get all evidence for an entity"""
    # Similar to relationship but for single entity
    evidences = []
    
    comms = db.query(Communication).filter(
        (Communication.source_phone.ilike(f"%{entity_id}%")) | (Communication.destination_phone.ilike(f"%{entity_id}%"))
    ).limit(20).all()
    
    for comm in comms:
        evidences.append({
            "type": "COMMUNICATION",
            "title": f"Communication: {comm.source_phone} → {comm.destination_phone}",
            "timestamp": comm.timestamp,
            "details": {"duration": comm.duration_seconds, "type": comm.communication_type}
        })
    
    return {"entity_id": entity_id, "evidences": evidences, "total": len(evidences)}
