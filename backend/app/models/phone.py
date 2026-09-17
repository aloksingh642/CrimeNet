from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Phone(Base):
    __tablename__ = "phones"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    owner_name = Column(String)
    carrier = Column(String)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
