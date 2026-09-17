"""
Graph Service - Builds graph from relational data
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..models.person import Person
from ..models.phone import Phone
from ..models.vehicle import Vehicle
from ..models.location import Location
from ..models.organization import Organization
from ..models.incident import Incident
from ..models.financial import FinancialAccount, Transaction
from ..models.communication import Communication
from ..models.evidence import Document
from .neo4j_client import graph_client
import json

class GraphService:
    def __init__(self):
        self.client = graph_client
    
    def build_full_graph(self, db: Session, limit_entities: int = 1000):
        """Build graph from all entities in DB"""
        self.client.clear_graph()
        
        # Persons
        persons = db.query(Person).limit(limit_entities).all()
        for p in persons:
            self.client.create_node("Person", {
                "id": f"person_{p.id}",
                "db_id": p.id,
                "name": p.name,
                "aliases": p.aliases,
                "gender": p.gender,
                "occupation": p.occupation,
                "risk_review_status": p.risk_review_status,
                "degree_centrality": p.degree_centrality,
                "community_id": p.community_id
            })
        
        # Phones
        phones = db.query(Phone).limit(limit_entities).all()
        for ph in phones:
            self.client.create_node("Phone", {
                "id": f"phone_{ph.id}",
                "db_id": ph.id,
                "phone_number": ph.phone_number,
                "owner_id": f"person_{ph.owner_id}" if ph.owner_id else None,
                "carrier": ph.carrier
            })
            if ph.owner_id:
                self.client.create_relationship(
                    f"person_{ph.owner_id}",
                    f"phone_{ph.id}",
                    "OWNS",
                    {"source": "phone_record", "confidence": 0.95}
                )
        
        # Vehicles
        vehicles = db.query(Vehicle).limit(limit_entities).all()
        for v in vehicles:
            self.client.create_node("Vehicle", {
                "id": f"vehicle_{v.id}",
                "db_id": v.id,
                "registration_number": v.registration_number,
                "vehicle_type": v.vehicle_type,
                "make": v.make,
                "model": v.model
            })
            if v.owner_id:
                self.client.create_relationship(
                    f"person_{v.owner_id}",
                    f"vehicle_{v.id}",
                    "OWNS",
                    {"source": "vehicle_record", "confidence": 0.9}
                )
        
        # Locations
        locations = db.query(Location).limit(limit_entities).all()
        for loc in locations:
            self.client.create_node("Location", {
                "id": f"location_{loc.id}",
                "db_id": loc.id,
                "name": loc.name,
                "address": loc.address,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "location_type": loc.location_type
            })
        
        # Organizations
        orgs = db.query(Organization).limit(limit_entities).all()
        for org in orgs:
            self.client.create_node("Organization", {
                "id": f"org_{org.id}",
                "db_id": org.id,
                "name": org.name,
                "type": org.type,
                "industry": org.industry
            })
        
        # Financial Accounts
        accounts = db.query(FinancialAccount).limit(limit_entities).all()
        for acc in accounts:
            self.client.create_node("FinancialAccount", {
                "id": f"account_{acc.id}",
                "db_id": acc.id,
                "masked_account_number": acc.masked_account_number,
                "institution": acc.institution,
                "owner_id": acc.owner_id
            })
            if acc.owner_id:
                self.client.create_relationship(
                    f"person_{acc.owner_id}",
                    f"account_{acc.id}",
                    "OWNS",
                    {"source": "financial_record", "confidence": 0.95}
                )
        
        # Communications -> relationships
        comms = db.query(Communication).limit(limit_entities*2).all()
        for comm in comms:
            src_id = f"phone_{comm.source_phone_id}" if comm.source_phone_id else f"phone_{comm.source_phone}"
            dst_id = f"phone_{comm.destination_phone_id}" if comm.destination_phone_id else f"phone_{comm.destination_phone}"
            # Ensure phone nodes exist for these numbers (if not already)
            # Create communication relationship
            self.client.create_relationship(
                src_id,
                dst_id,
                "CALLED",
                {
                    "timestamp": str(comm.timestamp) if comm.timestamp else "",
                    "duration": comm.duration_seconds,
                    "comm_type": comm.communication_type,
                    "source": "communication_record",
                    "confidence": 0.9,
                    "evidence_id": f"comm_{comm.id}"
                }
            )
            # Also person-person if owners known
            src_phone = db.query(Phone).filter(Phone.id == comm.source_phone_id).first() if comm.source_phone_id else None
            dst_phone = db.query(Phone).filter(Phone.id == comm.destination_phone_id).first() if comm.destination_phone_id else None
            if src_phone and dst_phone and src_phone.owner_id and dst_phone.owner_id:
                self.client.create_relationship(
                    f"person_{src_phone.owner_id}",
                    f"person_{dst_phone.owner_id}",
                    "COMMUNICATED_WITH",
                    {
                        "timestamp": str(comm.timestamp),
                        "duration": comm.duration_seconds,
                        "source": "communication_record",
                        "confidence": 0.85,
                        "evidence_id": f"comm_{comm.id}"
                    }
                )
        
        # Transactions -> relationships
        transactions = db.query(Transaction).limit(limit_entities*2).all()
        for txn in transactions:
            src_acc = f"account_{txn.sender_account_id}" if txn.sender_account_id else f"account_{txn.sender_account}"
            dst_acc = f"account_{txn.receiver_account_id}" if txn.receiver_account_id else f"account_{txn.receiver_account}"
            self.client.create_relationship(
                src_acc,
                dst_acc,
                "TRANSFERRED_TO",
                {
                    "amount": txn.amount,
                    "timestamp": str(txn.timestamp),
                    "txn_type": txn.transaction_type,
                    "source": "transaction_record",
                    "confidence": 0.95,
                    "evidence_id": f"txn_{txn.id}"
                }
            )
            # Person-person via accounts
            src_acc_obj = db.query(FinancialAccount).filter(FinancialAccount.id == txn.sender_account_id).first() if txn.sender_account_id else None
            dst_acc_obj = db.query(FinancialAccount).filter(FinancialAccount.id == txn.receiver_account_id).first() if txn.receiver_account_id else None
            if src_acc_obj and dst_acc_obj and src_acc_obj.owner_id and dst_acc_obj.owner_id:
                self.client.create_relationship(
                    f"person_{src_acc_obj.owner_id}",
                    f"person_{dst_acc_obj.owner_id}",
                    "FINANCIAL_LINK",
                    {
                        "amount": txn.amount,
                        "timestamp": str(txn.timestamp),
                        "source": "transaction_record",
                        "confidence": 0.9,
                        "evidence_id": f"txn_{txn.id}"
                    }
                )
        
        # Incidents -> relationships (simplified)
        incidents = db.query(Incident).limit(limit_entities).all()
        for inc in incidents:
            self.client.create_node("Incident", {
                "id": f"incident_{inc.id}",
                "db_id": inc.id,
                "incident_number": inc.incident_number,
                "incident_type": inc.incident_type,
                "location": inc.location,
                "description": inc.description
            })
        
        print(f"Graph built: {len(persons)} persons, {len(phones)} phones, {len(vehicles)} vehicles")
        return True
    
    def get_graph_data(self, filters: Dict[str, Any] = None, limit: int = 300):
        return self.client.get_graph(limit=limit, filters=filters)
    
    def find_path(self, source_id: str, target_id: str):
        # Normalize IDs - accept both raw db ids and prefixed ids
        # If numeric, try to find person
        if source_id.isdigit():
            source_id = f"person_{source_id}"
        if target_id.isdigit():
            target_id = f"person_{target_id}"
        return self.client.shortest_path(source_id, target_id)

graph_service = GraphService()
