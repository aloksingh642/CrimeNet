from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from ..database import Base

class Person(Base):
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    aliases = Column(Text, default="[]")  # JSON array
    date_of_birth = Column(String)  # synthetic, store as string
    gender = Column(String)
    occupation = Column(String)
    risk_review_status = Column(String, default="PENDING_REVIEW")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # For graph analytics cache
    degree_centrality = Column(Float, default=0.0)
    betweenness_centrality = Column(Float, default=0.0)
    closeness_centrality = Column(Float, default=0.0)
    pagerank = Column(Float, default=0.0)
    community_id = Column(Integer, default=-1)
