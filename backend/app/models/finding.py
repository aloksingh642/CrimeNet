from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from ..database import Base

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, nullable=True)
    finding_type = Column(String, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String, default="MEDIUM")
    confidence = Column(Float, default=0.8)
    status = Column(String, default="NEW")  # NEW, REVIEWED, FALSE_POSITIVE, SAVED
    evidence = Column(Text, default="{}")  # JSON with supporting evidence
    entities_involved = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
