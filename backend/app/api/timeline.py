from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models.incident import Incident
from ..models.communication import Communication
from ..models.financial import Transaction
from ..models.evidence import Document, Evidence
from ..models.user import User
from ..security.auth import get_current_active_user
from ..services.audit_service import log_audit

router = APIRouter(prefix="/api/timeline", tags=["timeline"])

@router.get("")
def get_timeline(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    entity_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    events = []
    
    # Incidents
    if not event_type or event_type == "INCIDENT":
        query = db.query(Incident)
        if start_date:
            try:
                sd = datetime.fromisoformat(start_date)
                query = query.filter(Incident.date >= sd)
            except:
                pass
        if end_date:
            try:
                ed = datetime.fromisoformat(end_date)
                query = query.filter(Incident.date <= ed)
            except:
                pass
        incidents = query.order_by(Incident.date.desc()).limit(limit//4).all()
        for inc in incidents:
            events.append({
                "id": f"incident_{inc.id}",
                "timestamp": inc.date.isoformat() if inc.date else inc.created_at.isoformat() if inc.created_at else datetime.utcnow().isoformat(),
                "event_type": "INCIDENT",
                "title": f"{inc.incident_type}: {inc.incident_number}",
                "description": inc.description[:200] if inc.description else "",
                "entities": [inc.location] if inc.location else [],
                "location": inc.location,
                "severity": inc.severity
            })
    
    # Communications
    if not event_type or event_type == "COMMUNICATION":
        query = db.query(Communication)
        if start_date:
            try:
                sd = datetime.fromisoformat(start_date)
                query = query.filter(Communication.timestamp >= sd)
            except:
                pass
        if end_date:
            try:
                ed = datetime.fromisoformat(end_date)
                query = query.filter(Communication.timestamp <= ed)
            except:
                pass
        comms = query.order_by(Communication.timestamp.desc()).limit(limit//4).all()
        for comm in comms:
            events.append({
                "id": f"comm_{comm.id}",
                "timestamp": comm.timestamp.isoformat() if comm.timestamp else datetime.utcnow().isoformat(),
                "event_type": "COMMUNICATION",
                "title": f"Call: {comm.source_phone} → {comm.destination_phone}",
                "description": f"{comm.communication_type} for {comm.duration_seconds}s",
                "entities": [comm.source_phone, comm.destination_phone],
                "location": comm.location
            })
    
    # Transactions
    if not event_type or event_type == "TRANSACTION":
        query = db.query(Transaction)
        if start_date:
            try:
                sd = datetime.fromisoformat(start_date)
                query = query.filter(Transaction.timestamp >= sd)
            except:
                pass
        if end_date:
            try:
                ed = datetime.fromisoformat(end_date)
                query = query.filter(Transaction.timestamp <= ed)
            except:
                pass
        txns = query.order_by(Transaction.timestamp.desc()).limit(limit//4).all()
        for txn in txns:
            events.append({
                "id": f"txn_{txn.id}",
                "timestamp": txn.timestamp.isoformat() if txn.timestamp else datetime.utcnow().isoformat(),
                "event_type": "TRANSACTION",
                "title": f"Transaction: ₹{txn.amount:,.2f}",
                "description": f"{txn.sender_account} → {txn.receiver_account} ({txn.transaction_type})",
                "entities": [txn.sender_account, txn.receiver_account],
                "location": txn.location
            })
    
    # Documents
    if not event_type or event_type == "DOCUMENT":
        query = db.query(Document)
        docs = query.order_by(Document.uploaded_at.desc()).limit(limit//4).all()
        for doc in docs:
            events.append({
                "id": f"doc_{doc.id}",
                "timestamp": doc.uploaded_at.isoformat() if doc.uploaded_at else datetime.utcnow().isoformat(),
                "event_type": "DOCUMENT",
                "title": f"Document: {doc.title}",
                "description": doc.text[:200] if doc.text else "",
                "entities": [],
                "location": None
            })
    
    # Sort by timestamp descending
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    log_audit(db, current_user.id, current_user.username, "TIMELINE_VIEWED", "TIMELINE", None, f"Viewed timeline with {len(events)} events")
    
    return {"events": events[:limit], "total": len(events)}

@router.get("/entity/{entity_id}")
def get_entity_timeline(entity_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # Simplified entity timeline - search for entity in all event types
    # entity_id could be person name, phone, etc.
    all_events = get_timeline(limit=200, db=db, current_user=current_user)
    
    filtered = []
    for event in all_events["events"]:
        # Check if entity_id appears in entities or description
        if entity_id.lower() in str(event.get("entities", [])).lower() or entity_id.lower() in event.get("title", "").lower() or entity_id.lower() in event.get("description", "").lower():
            filtered.append(event)
    
    return {"entity_id": entity_id, "events": filtered, "total": len(filtered)}
