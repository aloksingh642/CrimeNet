from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from ..database import Base

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    location_type = Column(String)
    risk_level = Column(String, default="LOW")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
