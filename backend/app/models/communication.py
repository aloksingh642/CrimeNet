from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from ..database import Base

class Communication(Base):
    __tablename__ = "communications"
    
    id = Column(Integer, primary_key=True, index=True)
    source_phone = Column(String, index=True, nullable=False)
    source_phone_id = Column(Integer, ForeignKey("phones.id"), nullable=True)
    destination_phone = Column(String, index=True, nullable=False)
    destination_phone_id = Column(Integer, ForeignKey("phones.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    duration_seconds = Column(Integer, default=0)
    communication_type = Column(String, default="CALL")
    location = Column(String)
