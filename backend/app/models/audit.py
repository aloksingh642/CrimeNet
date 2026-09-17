from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String)
    action = Column(String, index=True, nullable=False)
    resource_type = Column(String)
    resource_id = Column(String)
    details = Column(Text)
    ip_address = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
