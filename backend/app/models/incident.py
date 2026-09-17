from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from ..database import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_number = Column(String, unique=True, index=True, nullable=False)
    incident_type = Column(String, index=True)
    date = Column(DateTime(timezone=True))
    location = Column(String)
    location_id = Column(Integer, nullable=True)
    description = Column(Text)
    source = Column(String)
    severity = Column(String, default="MEDIUM")
    status = Column(String, default="OPEN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
