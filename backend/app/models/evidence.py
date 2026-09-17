from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

class Evidence(Base):
    __tablename__ = "evidences"
    
    id = Column(Integer, primary_key=True, index=True)
    evidence_type = Column(String, index=True)
    source = Column(String)
    reference_id = Column(String)
    case_id = Column(Integer, nullable=True)
    title = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    confidence = Column(String, default="HIGH")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String, index=True)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    source = Column(String)
    case_id = Column(Integer, nullable=True)
    uploaded_by = Column(String)
    entities_extracted = Column(Text, default="{}")  # JSON
    processing_status = Column(String, default="PENDING")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
