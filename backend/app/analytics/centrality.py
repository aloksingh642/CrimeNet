"""
Graph Analytics - Centrality, Communities, Anomalies
Uses NetworkX with fallback data
"""
from typing import Dict, List, Any
import networkx as nx
from collections import defaultdict, Counter
import math

class GraphAnalytics:
    def __init__(self):
        pass
    
    def build_nx_graph(self, graph_data: Dict[str, Any]) -> nx.Graph:
        """Build NetworkX graph from graph data"""
        G = nx.Graph()
        for node in graph_data.get("nodes", []):
            node_data = dict(node.get("properties", {}))
        node_data["label"] = node.get("label")
        node_data["type"] = node.get("type")
        G.add_node(node["id"], **node_data)
        for edge in graph_data.get("edges", []):
            G.add_edge(edge["source"], edge["target"], type=edge.get("type"), **edge.get("properties", {}))
        return G
    
    def calculate_centrality(self, graph_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Calculate various centrality measures"""
        G = self.build_nx_graph(graph_data)
        
        if len(G.nodes) == 0:
            return {"degree": [], "betweenness": [], "closeness": [], "pagerank": []}
        
        # Degree centrality
        try:
            degree = nx.degree_centrality(G)
        except:
            degree = {n: G.degree(n) / (len(G.nodes)-1) if len(G.nodes) > 1 else 0 for n in G.nodes}
        
        # Betweenness
        try:
            betweenness = nx.betweenness_centrality(G, k=min(100, len(G.nodes)), seed=42) if len(G.nodes) > 100 else nx.betweenness_centrality(G)
        except:
            betweenness = {n: 0 for n in G.nodes}
        
        # Closeness
        try:
            closeness = nx.closeness_centrality(G)
        except:
            closeness = {n: 0 for n in G.nodes}
        
        # PageRank
        try:
            pagerank = nx.pagerank(G, alpha=0.85)
        except:
            pagerank = {n: 1/len(G.nodes) for n in G.nodes}
        
        # Convert to sorted lists
        def to_sorted_list(centrality_dict, top_n=20):
            sorted_nodes = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
            result = []
            for node_id, score in sorted_nodes:
                node_data = next((n for n in graph_data["nodes"] if n["id"] == node_id), {})
                result.append({
                    "id": node_id,
                    "label": node_data.get("label", node_id),
                    "type": node_data.get("type", "Unknown"),
                    "score": round(score, 4),
                    "interpretation": self._interpret_centrality(score, "degree"),
                    "evidence": f"Connected to {G.degree(node_id)} entities directly"
                })
            return result
        
        return {
            "degree": to_sorted_list(degree),
            "betweenness": to_sorted_list(betweenness),
            "closeness": to_sorted_list(closeness),
            "pagerank": to_sorted_list(pagerank),
            "density": round(nx.density(G), 4),
            "components": nx.number_connected_components(G)
        }
    
    def _interpret_centrality(self, score: float, ctype: str) -> str:
        if score > 0.3:
            return "High network connectivity - potentially significant network position"
        elif score > 0.15:
            return "Moderate connectivity - requires investigator review"
        elif score > 0.05:
            return "Low-moderate connectivity"
        else:
            return "Low connectivity - peripheral position"
    
    def detect_communities(self, graph_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Community detection using greedy modularity"""
        G = self.build_nx_graph(graph_data)
        
        if len(G.nodes) == 0:
            return []
        
        try:
            # Use greedy modularity communities
            from networkx.algorithms import community
            communities = list(community.greedy_modularity_communities(G))
        except Exception as e:
            # Fallback: connected components as communities
            communities = list(nx.connected_components(G))
        
        result = []
        for idx, comm in enumerate(communities):
            comm_nodes = list(comm)
            subgraph = G.subgraph(comm_nodes)
            
            # Find central nodes in community
            try:
                degree_dict = dict(subgraph.degree())
                central = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:3]
                central_labels = []
                for node_id, deg in central:
                    node_data = next((n for n in graph_data["nodes"] if n["id"] == node_id), {})
                    central_labels.append(node_data.get("label", node_id))
            except:
                central_labels = []
            
            # Count types
            type_counts = Counter()
            for node_id in comm_nodes:
                node_data = next((n for n in graph_data["nodes"] if n["id"] == node_id), {})
                type_counts[node_data.get("type", "Unknown")] += 1
            
            result.append({
                "id": idx,
                "community_id": idx,
                "size": len(comm_nodes),
                "members": comm_nodes[:20],  # limit for display
                "member_count": len(comm_nodes),
                "edge_count": subgraph.number_of_edges(),
                "density": round(nx.density(subgraph), 4) if len(comm_nodes) > 1 else 0,
                "central_nodes": central_labels,
                "type_distribution": dict(type_counts),
                "description": f"Cluster with {len(comm_nodes)} entities and {subgraph.number_of_edges()} relationships"
            })
        
        # Sort by size descending
        result.sort(key=lambda x: x["size"], reverse=True)
        return result

analytics_service = GraphAnalytics()
