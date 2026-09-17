"""
NLP Pipeline for CrimeNet Intelligence
Uses regex + deterministic patterns + optional spaCy
Designed for synthetic demo data
"""
import re
from typing import Dict, List, Any
from datetime import datetime
import json

class NLPPipeline:
    def __init__(self):
        # Regex patterns for deterministic extraction
        self.phone_pattern = re.compile(r'(\+?91[-.\s]?)?[6-9]\d{9}|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
        self.vehicle_pattern = re.compile(r'\b[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{4}\b|\b[A-Z]{2}-\d{2}-[A-Z]{2}-\d{4}\b|\bHR26[A-Z]{1,2}\d{4}\b')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.date_pattern = re.compile(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b', re.IGNORECASE)
        self.account_pattern = re.compile(r'\b(?:ACCT|ACC|Account)[:\s]*[X*\d]{6,}\b|\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', re.IGNORECASE)
        self.amount_pattern = re.compile(r'(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?|\b\d+(?:,\d+)*(?:\.\d{2})?\s*(?:rupees|lakh|crore)\b', re.IGNORECASE)
        
        # Common Indian names for synthetic detection (demo dictionary)
        self.common_first_names = [
            "Rahul", "Amit", "Vikram", "Suresh", "Rajesh", "Priya", "Anjali", "Sunita",
            "Arjun", "Karan", "Rohan", "Sneha", "Pooja", "Neha", "Vijay", "Ajay",
            "Ramesh", "Mahesh", "Deepak", "Sanjay", "Manoj", "Anil", "Sunil", "Ravi"
        ]
        self.common_last_names = [
            "Sharma", "Verma", "Singh", "Kumar", "Patel", "Gupta", "Jain", "Yadav",
            "Reddy", "Nair", "Mehta", "Shah", "Malhotra", "Kapoor", "Chopra", "Bansal"
        ]
        
        # Try to load spaCy if available
        self.nlp = None
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Model not available, use blank
                self.nlp = spacy.blank("en")
                print("spaCy model en_core_web_sm not found, using blank model")
        except ImportError:
            print("spaCy not installed, using regex-only pipeline")
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities from text"""
        results = {
            "PERSON": [],
            "PHONE": [],
            "VEHICLE": [],
            "LOCATION": [],
            "ORGANIZATION": [],
            "DATE": [],
            "EMAIL": [],
            "FINANCIAL": [],
            "MONEY": []
        }
        
        # Phone numbers - regex
        for match in self.phone_pattern.finditer(text):
            results["PHONE"].append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.95,
                "source": "regex"
            })
        
        # Vehicles - regex
        for match in self.vehicle_pattern.finditer(text):
            results["VEHICLE"].append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.9,
                "source": "regex"
            })
        
        # Emails
        for match in self.email_pattern.finditer(text):
            results["EMAIL"].append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.95,
                "source": "regex"
            })
        
        # Dates
        for match in self.date_pattern.finditer(text):
            results["DATE"].append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.85,
                "source": "regex"
            })
        
        # Financial accounts
        for match in self.account_pattern.finditer(text):
            results["FINANCIAL"].append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.8,
                "source": "regex"
            })
        
        # Money
        for match in self.amount_pattern.finditer(text):
            results["MONEY"].append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.85,
                "source": "regex"
            })
        
        # Persons - using name dictionary + spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    results["PERSON"].append({
                        "text": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.85,
                        "source": "spacy"
                    })
                elif ent.label_ in ["GPE", "LOC"]:
                    results["LOCATION"].append({
                        "text": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.8,
                        "source": "spacy"
                    })
                elif ent.label_ == "ORG":
                    results["ORGANIZATION"].append({
                        "text": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.8,
                        "source": "spacy"
                    })
        
        # Fallback person detection via pattern: Capitalized First + Last
        person_pattern = re.compile(r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b')
        for match in person_pattern.finditer(text):
            full_name = match.group()
            # Check if looks like person name
            first, last = match.groups()
            if first in self.common_first_names or last in self.common_last_names or len(full_name.split()) == 2:
                # Avoid duplicate
                if not any(p["text"] == full_name for p in results["PERSON"]):
                    # Heuristic: if near keywords like "met", "seen", "observed", "named"
                    context_window = text[max(0, match.start()-50):min(len(text), match.end()+50)].lower()
                    if any(kw in context_window for kw in ["met", "seen", "observed", "named", "person", "mr.", "mr ", "identified", "suspect", "witness"]):
                        results["PERSON"].append({
                            "text": full_name,
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.75,
                            "source": "pattern"
                        })
        
        # Location keywords
        location_keywords = ["Market", "Nagar", "Colony", "Road", "Street", "Avenue", "Sector", "Park", "Mall", "Station", "Airport", "Hospital", "Bank", "Complex"]
        loc_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:' + '|'.join(location_keywords) + r'))\b')
        for match in loc_pattern.finditer(text):
            if not any(l["text"] == match.group() for l in results["LOCATION"]):
                results["LOCATION"].append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.7,
                    "source": "pattern"
                })
        
        return results
    
    def extract_relationships(self, text: str, entities: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []
        
        persons = entities.get("PERSON", [])
        locations = entities.get("LOCATION", [])
        vehicles = entities.get("VEHICLE", [])
        phones = entities.get("PHONE", [])
        
        # Person-Person associations (mentioned together)
        if len(persons) >= 2:
            for i in range(len(persons)):
                for j in range(i+1, len(persons)):
                    p1 = persons[i]
                    p2 = persons[j]
                    # If mentioned in same sentence or close proximity
                    distance = abs(p1["start"] - p2["start"])
                    if distance < 200:  # within 200 chars
                        relationships.append({
                            "source": p1["text"],
                            "source_type": "PERSON",
                            "target": p2["text"],
                            "target_type": "PERSON",
                            "relationship_type": "ASSOCIATED_WITH",
                            "confidence": 0.7 if distance < 100 else 0.5,
                            "evidence": f"Mentioned together within {distance} characters",
                            "text_snippet": text[max(0, min(p1["start"], p2["start"])-20):min(len(text), max(p1["end"], p2["end"])+20)]
                        })
        
        # Person-Location
        for person in persons:
            for loc in locations:
                distance = abs(person["start"] - loc["start"])
                if distance < 150:
                    relationships.append({
                        "source": person["text"],
                        "source_type": "PERSON",
                        "target": loc["text"],
                        "target_type": "LOCATION",
                        "relationship_type": "OBSERVED_AT",
                        "confidence": 0.65,
                        "evidence": f"Person and location mentioned in proximity",
                        "text_snippet": text[max(0, min(person["start"], loc["start"])-20):min(len(text), max(person["end"], loc["end"])+20)]
                    })
        
        # Person-Vehicle
        for person in persons:
            for vehicle in vehicles:
                distance = abs(person["start"] - vehicle["start"])
                if distance < 150:
                    relationships.append({
                        "source": person["text"],
                        "source_type": "PERSON",
                        "target": vehicle["text"],
                        "target_type": "VEHICLE",
                        "relationship_type": "ASSOCIATED_WITH",
                        "confidence": 0.6,
                        "evidence": "Person and vehicle mentioned together",
                        "text_snippet": text[max(0, min(person["start"], vehicle["start"])-20):min(len(text), max(person["end"], vehicle["end"])+20)]
                    })
        
        # Vehicle-Location
        for vehicle in vehicles:
            for loc in locations:
                distance = abs(vehicle["start"] - loc["start"])
                if distance < 150:
                    relationships.append({
                        "source": vehicle["text"],
                        "source_type": "VEHICLE",
                        "target": loc["text"],
                        "target_type": "LOCATION",
                        "relationship_type": "OBSERVED_AT",
                        "confidence": 0.65,
                        "evidence": "Vehicle and location mentioned together",
                        "text_snippet": text[max(0, min(vehicle["start"], loc["start"])-20):min(len(text), max(vehicle["end"], loc["end"])+20)]
                    })
        
        return relationships
    
    def process_document(self, text: str, doc_id: str = None) -> Dict[str, Any]:
        """Full pipeline: extract entities + relationships"""
        entities = self.extract_entities(text)
        relationships = self.extract_relationships(text, entities)
        
        return {
            "doc_id": doc_id,
            "text_length": len(text),
            "entities": entities,
            "relationships": relationships,
            "entity_counts": {k: len(v) for k, v in entities.items()},
            "relationship_count": len(relationships),
            "processed_at": datetime.utcnow().isoformat()
        }

# Singleton instance
nlp_pipeline = NLPPipeline()
