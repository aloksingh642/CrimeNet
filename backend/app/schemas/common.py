from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PersonResponse(BaseModel):
    id: int
    name: str
    aliases: str
    date_of_birth: Optional[str]
    gender: Optional[str]
    occupation: Optional[str]
    risk_review_status: str
    degree_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    pagerank: float = 0.0
    community_id: int = -1
    created_at: datetime
    
    class Config:
        from_attributes = True

class PhoneResponse(BaseModel):
    id: int
    phone_number: str
    owner_id: Optional[int]
    owner_name: Optional[str]
    carrier: Optional[str]
    status: str
    
    class Config:
        from_attributes = True

class VehicleResponse(BaseModel):
    id: int
    registration_number: str
    vehicle_type: Optional[str]
    make: Optional[str]
    model: Optional[str]
    owner_id: Optional[int]
    owner_name: Optional[str]
    
    class Config:
        from_attributes = True

class OrganizationResponse(BaseModel):
    id: int
    name: str
    type: Optional[str]
    industry: Optional[str]
    location: Optional[str]
    
    class Config:
        from_attributes = True

class LocationResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    location_type: Optional[str]
    
    class Config:
        from_attributes = True

class IncidentResponse(BaseModel):
    id: int
    incident_number: str
    incident_type: Optional[str]
    date: Optional[datetime]
    location: Optional[str]
    description: Optional[str]
    severity: str
    
    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: int
    transaction_id: str
    sender_account: str
    receiver_account: str
    amount: float
    timestamp: Optional[datetime]
    transaction_type: Optional[str]
    risk_flag: str
    
    class Config:
        from_attributes = True

class CommunicationResponse(BaseModel):
    id: int
    source_phone: str
    destination_phone: str
    timestamp: Optional[datetime]
    duration_seconds: int
    communication_type: str
    
    class Config:
        from_attributes = True

class DocumentCreate(BaseModel):
    title: str
    text: str
    document_type: str = "FIR"
    source: Optional[str] = None
    case_id: Optional[int] = None

class DocumentResponse(BaseModel):
    id: int
    document_type: str
    title: str
    text: str
    processing_status: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = {}

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: Dict[str, Any] = {}

class AnalyticsResponse(BaseModel):
    centrality: Dict[str, List[Dict[str, Any]]]
    communities: List[Dict[str, Any]]
    density: float
    components: int

class AnomalyResponse(BaseModel):
    id: int
    finding_type: str
    title: str
    description: str
    severity: str
    confidence: float
    status: str
    evidence: Dict[str, Any] = {}
    entities_involved: List[Any] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class TimelineEvent(BaseModel):
    id: str
    timestamp: datetime
    event_type: str
    title: str
    description: str
    entities: List[str] = []
    location: Optional[str] = None
    evidence_id: Optional[str] = None
