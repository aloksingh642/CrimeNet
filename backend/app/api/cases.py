from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random
from datetime import datetime
from ..database import get_db
from ..models.case import Case
from ..models.user import User
from ..schemas.case import CaseCreate, CaseUpdate, CaseResponse
from ..security.auth import get_current_active_user
from ..services.audit_service import log_audit

router = APIRouter(prefix="/api/cases", tags=["cases"])

@router.get("", response_model=List[CaseResponse])
def list_cases(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    cases = db.query(Case).order_by(Case.created_at.desc()).all()
    return cases

@router.post("", response_model=CaseResponse)
def create_case(case_data: CaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    case_number = case_data.case_number
    if not case_number:
        year = datetime.now().year
        count = db.query(Case).count() + 1
        case_number = f"CASE-{year}-{count:03d}"
    
    existing = db.query(Case).filter(Case.case_number == case_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Case number already exists")
    
    new_case = Case(
        case_number=case_number,
        title=case_data.title,
        description=case_data.description,
        status=case_data.status,
        priority=case_data.priority,
        investigator_id=current_user.id,
        investigator_name=current_user.full_name or current_user.username,
        associated_entities=str(case_data.associated_entities) if case_data.associated_entities else "{}"
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    log_audit(db, current_user.id, current_user.username, "CASE_CREATED", "CASE", new_case.id, f"Created case {case_number}")
    
    return new_case

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/{case_id}", response_model=CaseResponse)
def update_case(case_id: int, update_data: CaseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if update_data.title is not None:
        case.title = update_data.title
    if update_data.description is not None:
        case.description = update_data.description
    if update_data.status is not None:
        case.status = update_data.status
    if update_data.priority is not None:
        case.priority = update_data.priority
    if update_data.associated_entities is not None:
        case.associated_entities = str(update_data.associated_entities)
    
    db.commit()
    db.refresh(case)
    
    log_audit(db, current_user.id, current_user.username, "CASE_UPDATED", "CASE", case.id, f"Updated case {case.case_number}")
    
    return case

@router.delete("/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db.delete(case)
    db.commit()
    
    log_audit(db, current_user.id, current_user.username, "CASE_DELETED", "CASE", case_id, f"Deleted case {case.case_number}")
    
    return {"message": "Case deleted"}
