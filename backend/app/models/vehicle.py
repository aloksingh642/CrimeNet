from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String, unique=True, index=True, nullable=False)
    vehicle_type = Column(String)
    make = Column(String)
    model = Column(String)
    color = Column(String)
    owner_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    owner_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
