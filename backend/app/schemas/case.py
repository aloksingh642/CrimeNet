from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class CaseCreate(BaseModel):
    case_number: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str = "OPEN"
    priority: str = "MEDIUM"
    associated_entities: Optional[Dict[str, Any]] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    associated_entities: Optional[Dict[str, Any]] = None

class CaseResponse(BaseModel):
    id: int
    case_number: str
    title: str
    description: Optional[str]
    status: str
    investigator_id: Optional[int]
    investigator_name: Optional[str]
    priority: str
    created_at: datetime
    associated_entities: Optional[str] = None
    
    class Config:
        from_attributes = True
