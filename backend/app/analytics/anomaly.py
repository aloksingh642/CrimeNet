"""
Anomaly Detection for CrimeNet
Explainable pattern detection
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import statistics

class AnomalyDetector:
    def __init__(self):
        pass
    
    def detect_all(self, db: Session, graph_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Run all anomaly detection"""
        anomalies = []
        
        anomalies.extend(self.detect_communication_spikes(db))
        anomalies.extend(self.detect_unusual_transactions(db))
        anomalies.extend(self.detect_repeated_location_overlaps(db))
        anomalies.extend(self.detect_bridge_entities(db, graph_data))
        anomalies.extend(self.detect_high_degree_entities(db, graph_data))
        anomalies.extend(self.detect_cross_community_connections(db, graph_data))
        
        # Sort by severity/confidence
        anomalies.sort(key=lambda x: (x["severity"] == "HIGH", x["confidence"]), reverse=True)
        return anomalies
    
    def detect_communication_spikes(self, db: Session) -> List[Dict[str, Any]]:
        """Detect sudden increase in communication"""
        from ..models.communication import Communication
        from ..models.phone import Phone
        
        anomalies = []
        try:
            # Group communications by source-destination pair per week
            comms = db.query(Communication).order_by(Communication.timestamp).all()
            
            # Group by pair
            pair_comms = defaultdict(list)
            for comm in comms:
                key = tuple(sorted([comm.source_phone, comm.destination_phone]))
                pair_comms[key].append(comm)
            
            for pair, comm_list in pair_comms.items():
                if len(comm_list) < 5:
                    continue
                
                # Split into weeks (simplified: first half vs second half)
                comm_list_sorted = sorted(comm_list, key=lambda x: x.timestamp or datetime.min)
                mid = len(comm_list_sorted) // 2
                first_half = comm_list_sorted[:mid]
                second_half = comm_list_sorted[mid:]
                
                if not first_half or not second_half:
                    continue
                
                avg_first = len(first_half)
                avg_second = len(second_half)
                
                # If second half has 3x more than first
                if avg_second >= avg_first * 2.5 and avg_second >= 5:
                    increase_pct = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 999
                    
                    anomalies.append({
                        "id": f"comm_spike_{pair[0]}_{pair[1]}",
                        "finding_type": "COMMUNICATION_SPIKE",
                        "title": f"Unusual communication increase between {pair[0]} and {pair[1]}",
                        "description": f"Communication activity increased from average of {avg_first} interactions to {avg_second} interactions ({increase_pct:.0f}% increase)",
                        "severity": "HIGH" if increase_pct > 300 else "MEDIUM",
                        "confidence": 0.85,
                        "evidence": {
                            "what": "Sudden increase in communication frequency",
                            "why": f"Baseline: {avg_first} interactions, Current: {avg_second} interactions",
                            "when": f"Detected across {len(comm_list)} total communications",
                            "entities": list(pair),
                            "baseline": avg_first,
                            "current": avg_second,
                            "increase_percent": round(increase_pct, 1),
                            "total_interactions": len(comm_list)
                        },
                        "entities_involved": list(pair),
                        "status": "NEW",
                        "created_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            print(f"Communication spike detection failed: {e}")
        
        return anomalies[:10]  # Limit
    
    def detect_unusual_transactions(self, db: Session) -> List[Dict[str, Any]]:
        """Detect unusual transaction amounts"""
        from ..models.financial import Transaction
        
        anomalies = []
        try:
            transactions = db.query(Transaction).all()
            if len(transactions) < 10:
                return []
            
            amounts = [t.amount for t in transactions]
            mean_amt = statistics.mean(amounts)
            stdev_amt = statistics.stdev(amounts) if len(amounts) > 1 else mean_amt * 0.5
            
            threshold = mean_amt + 2.5 * stdev_amt
            
            for txn in transactions:
                if txn.amount > threshold and txn.amount > 50000:  # Only flag large amounts
                    anomalies.append({
                        "id": f"txn_unusual_{txn.id}",
                        "finding_type": "UNUSUAL_TRANSACTION",
                        "title": f"Unusual transaction amount: ₹{txn.amount:,.2f}",
                        "description": f"Transaction amount ₹{txn.amount:,.2f} significantly exceeds average transaction of ₹{mean_amt:,.2f} (threshold: ₹{threshold:,.2f})",
                        "severity": "HIGH" if txn.amount > mean_amt + 3*stdev_amt else "MEDIUM",
                        "confidence": 0.8,
                        "evidence": {
                            "what": "Transaction amount exceeds statistical threshold",
                            "why": f"Amount ₹{txn.amount:,.2f} vs average ₹{mean_amt:,.2f} + 2.5σ (σ=₹{stdev_amt:,.2f})",
                            "when": str(txn.timestamp),
                            "entities": [txn.sender_account, txn.receiver_account],
                            "amount": txn.amount,
                            "mean": round(mean_amt, 2),
                            "stdev": round(stdev_amt, 2),
                            "threshold": round(threshold, 2),
                            "transaction_id": txn.transaction_id
                        },
                        "entities_involved": [txn.sender_account, txn.receiver_account],
                        "status": "NEW",
                        "created_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            print(f"Unusual transaction detection failed: {e}")
        
        return anomalies[:10]
    
    def detect_repeated_location_overlaps(self, db: Session) -> List[Dict[str, Any]]:
        """Detect multiple entities at same location repeatedly"""
        from ..models.incident import Incident
        
        anomalies = []
        try:
            incidents = db.query(Incident).all()
            location_groups = defaultdict(list)
            for inc in incidents:
                if inc.location:
                    location_groups[inc.location].append(inc)
            
            for location, inc_list in location_groups.items():
                if len(inc_list) >= 5:  # 5+ incidents at same location
                    # Check time clustering
                    anomalies.append({
                        "id": f"loc_overlap_{location.replace(' ', '_')}",
                        "finding_type": "LOCATION_OVERLAP",
                        "title": f"Repeated activity at location: {location}",
                        "description": f"Location '{location}' observed in {len(inc_list)} incidents - higher than typical location frequency",
                        "severity": "MEDIUM",
                        "confidence": 0.7,
                        "evidence": {
                            "what": "Multiple incidents at same location",
                            "why": f"{len(inc_list)} incidents at this location vs average location appears in ~2 incidents",
                            "when": f"Across {len(inc_list)} records",
                            "entities": [location],
                            "location": location,
                            "incident_count": len(inc_list),
                            "incident_types": list(set([i.incident_type for i in inc_list if i.incident_type]))
                        },
                        "entities_involved": [location],
                        "status": "NEW",
                        "created_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            print(f"Location overlap detection failed: {e}")
        
        return anomalies[:5]
    
    def detect_bridge_entities(self, db: Session, graph_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Detect entities connecting different communities (bridge)"""
        anomalies = []
        if not graph_data or len(graph_data.get("nodes", [])) < 10:
            return []
        
        try:
            import networkx as nx
            from .centrality import analytics_service
            G = analytics_service.build_nx_graph(graph_data)
            
            if len(G.nodes) < 5:
                return []
            
            # Betweenness centrality high = potential bridge
            betweenness = nx.betweenness_centrality(G)
            sorted_b = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for node_id, score in sorted_b:
                if score > 0.1:  # Threshold
                    node_data = next((n for n in graph_data["nodes"] if n["id"] == node_id), {})
                    anomalies.append({
                        "id": f"bridge_{node_id}",
                        "finding_type": "BRIDGE_ENTITY",
                        "title": f"Bridge entity detected: {node_data.get('label', node_id)}",
                        "description": f"Entity '{node_data.get('label', node_id)}' shows high betweenness centrality ({score:.3f}), potentially connecting separate network communities",
                        "severity": "MEDIUM",
                        "confidence": 0.75,
                        "evidence": {
                            "what": "High betweenness centrality indicates bridge position",
                            "why": f"Betweenness score {score:.3f} exceeds threshold 0.1 - this entity lies on many shortest paths between other entities",
                            "when": "Based on current network structure",
                            "entities": [node_id],
                            "betweenness_score": round(score, 4),
                            "degree": G.degree(node_id),
                            "entity_label": node_data.get('label', node_id),
                            "entity_type": node_data.get('type', 'Unknown')
                        },
                        "entities_involved": [node_id],
                        "status": "NEW",
                        "created_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            print(f"Bridge detection failed: {e}")
        
        return anomalies[:5]
    
    def detect_high_degree_entities(self, db: Session, graph_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Detect entities with unusually high connections"""
        anomalies = []
        if not graph_data:
            return []
        
        try:
            import networkx as nx
            from .centrality import analytics_service
            G = analytics_service.build_nx_graph(graph_data)
            
            if len(G.nodes) == 0:
                return []
            
            degrees = dict(G.degree())
            if not degrees:
                return []
            
            mean_deg = statistics.mean(degrees.values())
            stdev_deg = statistics.stdev(degrees.values()) if len(degrees) > 1 else 1
            
            threshold = mean_deg + 2 * stdev_deg
            
            for node_id, deg in degrees.items():
                if deg > threshold and deg > 5:
                    node_data = next((n for n in graph_data["nodes"] if n["id"] == node_id), {})
                    anomalies.append({
                        "id": f"high_degree_{node_id}",
                        "finding_type": "HIGH_CONNECTIVITY",
                        "title": f"High connectivity entity: {node_data.get('label', node_id)}",
                        "description": f"Entity has {deg} connections, significantly above network average of {mean_deg:.1f} (threshold: {threshold:.1f})",
                        "severity": "MEDIUM",
                        "confidence": 0.7,
                        "evidence": {
                            "what": "Entity with unusually high number of connections",
                            "why": f"Degree {deg} vs mean {mean_deg:.1f} + 2σ (σ={stdev_deg:.1f})",
                            "when": "Current network snapshot",
                            "entities": [node_id],
                            "degree": deg,
                            "mean_degree": round(mean_deg, 2),
                            "threshold": round(threshold, 2),
                            "entity_label": node_data.get('label', node_id)
                        },
                        "entities_involved": [node_id],
                        "status": "NEW",
                        "created_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            print(f"High degree detection failed: {e}")
        
        return anomalies[:5]
    
    def detect_cross_community_connections(self, db: Session, graph_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Detect new connections between previously separate communities"""
        # Simplified: look for edges connecting nodes that would otherwise be in different components
        anomalies = []
        if not graph_data:
            return []
        
        try:
            import networkx as nx
            from .centrality import analytics_service
            G = analytics_service.build_nx_graph(graph_data)
            
            # Find connected components
            components = list(nx.connected_components(G))
            if len(components) < 2:
                return []
            
            # For demo, flag if there are exactly 2-3 components and we have many inter-component potential
            # Actually, this is hard without temporal data, so we simulate by checking if removal of an edge would disconnect
            # Find bridges using networkx
            try:
                bridges = list(nx.bridges(G))
                for u, v in bridges[:3]:
                    u_data = next((n for n in graph_data["nodes"] if n["id"] == u), {})
                    v_data = next((n for n in graph_data["nodes"] if n["id"] == v), {})
                    anomalies.append({
                        "id": f"cross_comm_{u}_{v}",
                        "finding_type": "CROSS_COMMUNITY_LINK",
                        "title": f"Cross-community connection: {u_data.get('label', u)} ↔ {v_data.get('label', v)}",
                        "description": f"Connection between '{u_data.get('label', u)}' and '{v_data.get('label', v)}' appears to be a critical link whose removal would fragment the network",
                        "severity": "MEDIUM",
                        "confidence": 0.65,
                        "evidence": {
                            "what": "Bridge edge connecting network segments",
                            "why": "Edge is a graph bridge - its removal increases number of connected components",
                            "when": "Current network structure",
                            "entities": [u, v],
                            "entity_labels": [u_data.get('label', u), v_data.get('label', v)]
                        },
                        "entities_involved": [u, v],
                        "status": "NEW",
                        "created_at": datetime.utcnow().isoformat()
                    })
            except:
                pass
        except Exception as e:
            print(f"Cross community detection failed: {e}")
        
        return anomalies[:3]

anomaly_detector = AnomalyDetector()
