"""
Entity Resolution for CrimeNet
Detects possible duplicate entities using fuzzy matching
"""
from typing import List, Dict, Any, Tuple
import re
from difflib import SequenceMatcher
from collections import defaultdict

class EntityResolver:
    def __init__(self):
        self.threshold = 0.75
    
    def normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        # Lowercase, remove extra spaces, remove titles
        name = name.lower().strip()
        name = re.sub(r'\b(mr|mrs|ms|dr|prof)\.?\s+', '', name)
        name = re.sub(r'\s+', ' ', name)
        # Remove non-alpha except space
        name = re.sub(r'[^a-z\s]', '', name)
        return name.strip()
    
    def name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Exact match
        if norm1 == norm2:
            return 1.0
        
        # Token-based similarity
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        jaccard = len(intersection) / len(union) if union else 0
        
        # Sequence matcher
        seq_ratio = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Initials matching: "R. Sharma" vs "Rahul Sharma"
        initial_match = 0.0
        if len(tokens1) == 2 and len(tokens2) == 2:
            # Check if one is initial
            for t1, t2 in [(tokens1, tokens2), (tokens2, tokens1)]:
                t1_list = list(t1)
                t2_list = list(t2)
                # One token is single char
                if any(len(t) == 1 for t in t1_list):
                    # Check if initial matches first char of other
                    for tok1 in t1_list:
                        if len(tok1) == 1:
                            for tok2 in t2_list:
                                if tok2.startswith(tok1):
                                    initial_match = max(initial_match, 0.8)
        
        # Combined score
        combined = (jaccard * 0.4 + seq_ratio * 0.4 + initial_match * 0.2)
        # Boost if last name matches
        last1 = norm1.split()[-1] if norm1.split() else ""
        last2 = norm2.split()[-1] if norm2.split() else ""
        if last1 and last2 and last1 == last2:
            combined = min(1.0, combined + 0.15)
        
        return combined
    
    def phone_similarity(self, phone1: str, phone2: str) -> float:
        """Compare phone numbers (normalized)"""
        def normalize_phone(p):
            return re.sub(r'\D', '', p)[-10:]  # last 10 digits
        
        n1 = normalize_phone(phone1)
        n2 = normalize_phone(phone2)
        return 1.0 if n1 == n2 and len(n1) >= 7 else 0.0
    
    def find_duplicates(self, persons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find possible duplicate persons
        persons: list of dicts with at least id, name, and optional phone, vehicle
        """
        duplicates = []
        checked = set()
        
        for i in range(len(persons)):
            for j in range(i+1, len(persons)):
                pair_key = tuple(sorted([persons[i]['id'], persons[j]['id']]))
                if pair_key in checked:
                    continue
                checked.add(pair_key)
                
                p1 = persons[i]
                p2 = persons[j]
                
                name_sim = self.name_similarity(p1.get('name', ''), p2.get('name', ''))
                
                evidence = []
                score = name_sim
                evidence.append(f"Name similarity: {name_sim:.2f} ('{p1.get('name')}' vs '{p2.get('name')}')")
                
                # Check additional signals if available
                if p1.get('phone') and p2.get('phone'):
                    phone_sim = self.phone_similarity(p1['phone'], p2['phone'])
                    if phone_sim > 0:
                        score = min(1.0, score + 0.2)
                        evidence.append(f"Same phone association: {p1['phone']}")
                
                if p1.get('vehicle') and p2.get('vehicle') and p1['vehicle'] == p2['vehicle']:
                    score = min(1.0, score + 0.15)
                    evidence.append(f"Same vehicle: {p1['vehicle']}")
                
                if p1.get('location') and p2.get('location') and p1['location'] == p2['location']:
                    score = min(1.0, score + 0.05)
                    evidence.append(f"Same location: {p1['location']}")
                
                if score >= self.threshold:
                    duplicates.append({
                        "entity1_id": p1['id'],
                        "entity1_name": p1.get('name'),
                        "entity2_id": p2['id'],
                        "entity2_name": p2.get('name'),
                        "similarity_score": round(score, 3),
                        "confidence": "HIGH" if score > 0.85 else "MEDIUM" if score > 0.75 else "LOW",
                        "evidence": evidence,
                        "status": "PENDING_REVIEW",
                        "recommendation": "Possible duplicate - requires investigator review"
                    })
        
        # Sort by similarity descending
        duplicates.sort(key=lambda x: x['similarity_score'], reverse=True)
        return duplicates
    
    def resolve_entities(self, all_entities: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Resolve across all entity types"""
        result = {
            "person_duplicates": [],
            "phone_duplicates": [],
            "vehicle_duplicates": [],
            "total_possible_duplicates": 0
        }
        
        if "persons" in all_entities:
            result["person_duplicates"] = self.find_duplicates(all_entities["persons"])
        
        # For phones, check exact number matches with different owners
        if "phones" in all_entities:
            phone_map = defaultdict(list)
            for phone in all_entities["phones"]:
                norm = re.sub(r'\D', '', phone.get('phone_number', ''))[-10:]
                phone_map[norm].append(phone)
            
            for norm, phones in phone_map.items():
                if len(phones) > 1:
                    owners = set(p.get('owner_name') for p in phones)
                    if len(owners) > 1:
                        result["phone_duplicates"].append({
                            "phone_number": norm,
                            "count": len(phones),
                            "owners": list(owners),
                            "evidence": f"Same phone number associated with multiple owners: {', '.join(owners)}",
                            "status": "REQUIRES_REVIEW"
                        })
        
        result["total_possible_duplicates"] = len(result["person_duplicates"]) + len(result["phone_duplicates"])
        return result

entity_resolver = EntityResolver()
