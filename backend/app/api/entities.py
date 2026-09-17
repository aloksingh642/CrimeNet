from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from ..database import get_db
from ..models.person import Person
from ..models.phone import Phone
from ..models.vehicle import Vehicle
from ..models.organization import Organization
from ..models.location import Location
from ..models.incident import Incident
from ..models.financial import FinancialAccount, Transaction
from ..models.communication import Communication
from ..models.user import User
from ..security.auth import get_current_active_user
from ..services.audit_service import log_audit

router = APIRouter(prefix="/api/entities", tags=["entities"])

@router.get("/search")
def search_entities(
    q: str = Query(..., min_length=1),
    entity_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    results = {
        "persons": [],
        "phones": [],
        "vehicles": [],
        "organizations": [],
        "locations": [],
        "incidents": []
    }
    
    search_term = f"%{q}%"
    
    if not entity_type or entity_type == "PERSON":
        persons = db.query(Person).filter(Person.name.ilike(search_term)).limit(limit).all()
        results["persons"] = [{"id": p.id, "name": p.name, "type": "PERSON", "occupation": p.occupation, "risk_review_status": p.risk_review_status} for p in persons]
    
    if not entity_type or entity_type == "PHONE":
        phones = db.query(Phone).filter(Phone.phone_number.ilike(search_term)).limit(limit).all()
        results["phones"] = [{"id": p.id, "phone_number": p.phone_number, "type": "PHONE", "owner_name": p.owner_name} for p in phones]
    
    if not entity_type or entity_type == "VEHICLE":
        vehicles = db.query(Vehicle).filter(Vehicle.registration_number.ilike(search_term)).limit(limit).all()
        results["vehicles"] = [{"id": v.id, "registration_number": v.registration_number, "type": "VEHICLE", "owner_name": v.owner_name} for v in vehicles]
    
    if not entity_type or entity_type == "ORGANIZATION":
        orgs = db.query(Organization).filter(Organization.name.ilike(search_term)).limit(limit).all()
        results["organizations"] = [{"id": o.id, "name": o.name, "type": "ORGANIZATION", "industry": o.industry} for o in orgs]
    
    if not entity_type or entity_type == "LOCATION":
        locs = db.query(Location).filter(Location.name.ilike(search_term)).limit(limit).all()
        results["locations"] = [{"id": l.id, "name": l.name, "type": "LOCATION", "address": l.address} for l in locs]
    
    if not entity_type or entity_type == "INCIDENT":
        incidents = db.query(Incident).filter(or_(Incident.incident_number.ilike(search_term), Incident.description.ilike(search_term))).limit(limit).all()
        results["incidents"] = [{"id": i.id, "incident_number": i.incident_number, "type": "INCIDENT", "incident_type": i.incident_type} for i in incidents]
    
    total = sum(len(v) for v in results.values())
    
    log_audit(db, current_user.id, current_user.username, "ENTITY_SEARCH", "SEARCH", None, f"Searched for '{q}' - found {total} results")
    
    return {"query": q, "total": total, "results": results}

@router.get("/person/{person_id}")
def get_person(person_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Get related entities
    phones = db.query(Phone).filter(Phone.owner_id == person_id).all()
    vehicles = db.query(Vehicle).filter(Vehicle.owner_id == person_id).all()
    accounts = db.query(FinancialAccount).filter(FinancialAccount.owner_id == person_id).all()
    
    # Communications via phones
    phone_ids = [p.id for p in phones]
    comms = []
    if phone_ids:
        comms = db.query(Communication).filter(
            or_(Communication.source_phone_id.in_(phone_ids), Communication.destination_phone_id.in_(phone_ids))
        ).limit(20).all()
    
    # Transactions via accounts
    account_ids = [a.id for a in accounts]
    txns = []
    if account_ids:
        txns = db.query(Transaction).filter(
            or_(Transaction.sender_account_id.in_(account_ids), Transaction.receiver_account_id.in_(account_ids))
        ).limit(20).all()
    
    return {
        "person": {
            "id": person.id,
            "name": person.name,
            "aliases": person.aliases,
            "date_of_birth": person.date_of_birth,
            "gender": person.gender,
            "occupation": person.occupation,
            "risk_review_status": person.risk_review_status,
            "degree_centrality": person.degree_centrality,
            "betweenness_centrality": person.betweenness_centrality,
            "pagerank": person.pagerank,
            "community_id": person.community_id
        },
        "phones": [{"id": p.id, "phone_number": p.phone_number, "carrier": p.carrier} for p in phones],
        "vehicles": [{"id": v.id, "registration_number": v.registration_number, "vehicle_type": v.vehicle_type} for v in vehicles],
        "accounts": [{"id": a.id, "masked_account_number": a.masked_account_number, "institution": a.institution} for a in accounts],
        "recent_communications": [{"id": c.id, "source": c.source_phone, "dest": c.destination_phone, "timestamp": c.timestamp} for c in comms],
        "recent_transactions": [{"id": t.id, "amount": t.amount, "sender": t.sender_account, "receiver": t.receiver_account, "timestamp": t.timestamp} for t in txns]
    }

@router.get("/stats")
def get_entity_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    stats = {
        "persons": db.query(Person).count(),
        "phones": db.query(Phone).count(),
        "vehicles": db.query(Vehicle).count(),
        "organizations": db.query(Organization).count(),
        "locations": db.query(Location).count(),
        "incidents": db.query(Incident).count(),
        "transactions": db.query(Transaction).count(),
        "communications": db.query(Communication).count(),
    }
    return stats

@router.get("/persons")
def list_persons(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    persons = db.query(Person).offset(skip).limit(limit).all()
    return [{"id": p.id, "name": p.name, "occupation": p.occupation, "risk_review_status": p.risk_review_status, "community_id": p.community_id, "degree_centrality": p.degree_centrality} for p in persons]

@router.get("/phones")
def list_phones(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    phones = db.query(Phone).offset(skip).limit(limit).all()
    return [{"id": p.id, "phone_number": p.phone_number, "owner_name": p.owner_name, "carrier": p.carrier} for p in phones]

@router.get("/vehicles")
def list_vehicles(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    vehicles = db.query(Vehicle).offset(skip).limit(limit).all()
    return [{"id": v.id, "registration_number": v.registration_number, "vehicle_type": v.vehicle_type, "owner_name": v.owner_name} for v in vehicles]
