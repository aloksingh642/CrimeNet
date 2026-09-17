from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.evidence import Document, Evidence
from ..models.user import User
from ..security.auth import get_current_active_user
from ..schemas.common import DocumentCreate, DocumentResponse
from ..ai.nlp_pipeline import nlp_pipeline
from ..services.audit_service import log_audit
import json

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).limit(100).all()
    return docs

@router.post("", response_model=DocumentResponse)
def create_document(doc_data: DocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    new_doc = Document(
        title=doc_data.title,
        text=doc_data.text,
        document_type=doc_data.document_type,
        source=doc_data.source,
        case_id=doc_data.case_id,
        uploaded_by=current_user.username,
        processing_status="PENDING"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    log_audit(db, current_user.id, current_user.username, "DOCUMENT_UPLOADED", "DOCUMENT", new_doc.id, f"Uploaded document {new_doc.title}")
    
    return new_doc

@router.post("/upload")
def upload_document(file: UploadFile = File(...), case_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    content = file.file.read().decode('utf-8', errors='ignore')
    
    new_doc = Document(
        title=file.filename,
        text=content[:10000],  # limit
        document_type="UPLOADED",
        source="file_upload",
        case_id=case_id,
        uploaded_by=current_user.username,
        processing_status="PENDING"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    log_audit(db, current_user.id, current_user.username, "DOCUMENT_UPLOADED", "DOCUMENT", new_doc.id, f"Uploaded file {file.filename}")
    
    return {"id": new_doc.id, "title": new_doc.title, "status": "uploaded"}

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/{doc_id}/process")
def process_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Run NLP pipeline
    result = nlp_pipeline.process_document(doc.text, doc_id=str(doc.id))
    
    # Save extracted entities
    doc.entities_extracted = json.dumps(result)
    doc.processing_status = "PROCESSED"
    db.commit()
    
    log_audit(db, current_user.id, current_user.username, "DOCUMENT_PROCESSED", "DOCUMENT", doc.id, f"Processed document with {result['relationship_count']} relationships")
    
    return result

@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(doc)
    db.commit()
    
    log_audit(db, current_user.id, current_user.username, "DOCUMENT_DELETED", "DOCUMENT", doc_id, f"Deleted document {doc.title}")
    
    return {"message": "Document deleted"}
