"""
Neo4j Client with fallback to NetworkX in-memory graph
"""
from typing import List, Dict, Any, Optional
import os
from ..config import settings

class GraphClient:
    def __init__(self):
        self.driver = None
        self.use_neo4j = False
        self.memory_graph = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Neo4j or fallback to NetworkX"""
        try:
            from neo4j import GraphDatabase
            # Try to connect
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # Test connection
            self.driver.verify_connectivity()
            self.use_neo4j = True
            print(f"Connected to Neo4j at {settings.NEO4J_URI}")
        except Exception as e:
            print(f"Neo4j connection failed ({e}), using in-memory NetworkX graph")
            self.use_neo4j = False
            try:
                import networkx as nx
                self.memory_graph = nx.MultiDiGraph()
            except ImportError:
                self.memory_graph = None
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def clear_graph(self):
        if self.use_neo4j and self.driver:
            try:
                with self.driver.session() as session:
                    session.run("MATCH (n) DETACH DELETE n")
            except Exception as e:
                print(f"Failed to clear Neo4j: {e}")
        if self.memory_graph is not None:
            self.memory_graph.clear()
    
    def create_node(self, label: str, properties: Dict[str, Any]):
        """Create a node"""
        if self.use_neo4j and self.driver:
            try:
                with self.driver.session() as session:
                    # Create with MERGE to avoid duplicates
                    props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
                    query = f"MERGE (n:{label} {{{props_str}}}) RETURN n"
                    # Ensure id is present
                    session.run(query, **properties)
                    return True
            except Exception as e:
                print(f"Neo4j create_node failed: {e}")
                # Fallback to memory
                self.use_neo4j = False
        
        # In-memory fallback
        if self.memory_graph is not None:
            import networkx as nx
            node_id = properties.get('id', f"{label}_{len(self.memory_graph.nodes)}")
            self.memory_graph.add_node(node_id, label=label, **properties)
            return True
        return False
    
    def create_relationship(self, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any] = None):
        """Create relationship"""
        properties = properties or {}
        
        if self.use_neo4j and self.driver:
            try:
                with self.driver.session() as session:
                    query = """
                    MATCH (a {id: $source_id}), (b {id: $target_id})
                    MERGE (a)-[r:%s]->(b)
                    SET r += $props
                    RETURN r
                    """ % rel_type
                    session.run(query, source_id=source_id, target_id=target_id, props=properties)
                    return True
            except Exception as e:
                print(f"Neo4j create_relationship failed: {e}")
                self.use_neo4j = False
        
        if self.memory_graph is not None:
            edge_props = dict(properties)
            edge_props['type'] = rel_type
            self.memory_graph.add_edge(source_id, target_id, **edge_props)
            return True
        return False
    
    def get_graph(self, limit: int = 500, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get graph data for visualization"""
        filters = filters or {}
        
        if self.use_neo4j and self.driver:
            try:
                with self.driver.session() as session:
                    # Build query with filters
                    where_clauses = []
                    if filters.get('node_type'):
                        where_clauses.append(f"n:{filters['node_type']}")
                    if filters.get('relationship_type'):
                        rel_filter = filters['relationship_type']
                        match_query = f"MATCH (n)-[r:{rel_filter}]->(m)"
                    else:
                        match_query = "MATCH (n)-[r]->(m)"
                    
                    query = f"""
                    {match_query}
                    RETURN n, r, m
                    LIMIT $limit
                    """
                    result = session.run(query, limit=limit)
                    
                    nodes = {}
                    edges = []
                    for record in result:
                        n = record['n']
                        m = record['m']
                        r = record['r']
                        
                        n_id = n.get('id', str(n.element_id))
                        m_id = m.get('id', str(m.element_id))
                        
                        if n_id not in nodes:
                            nodes[n_id] = {
                                "id": n_id,
                                "label": n.get('name', n.get('phone_number', n.get('registration_number', n_id))),
                                "type": list(n.labels)[0] if hasattr(n, 'labels') else 'Unknown',
                                "properties": dict(n)
                            }
                        if m_id not in nodes:
                            nodes[m_id] = {
                                "id": m_id,
                                "label": m.get('name', m.get('phone_number', m.get('registration_number', m_id))),
                                "type": list(m.labels)[0] if hasattr(m, 'labels') else 'Unknown',
                                "properties": dict(m)
                            }
                        
                        edges.append({
                            "id": f"{n_id}_{m_id}_{len(edges)}",
                            "source": n_id,
                            "target": m_id,
                            "type": r.type if hasattr(r, 'type') else 'RELATED',
                            "properties": dict(r)
                        })
                    
                    return {
                        "nodes": list(nodes.values()),
                        "edges": edges,
                        "stats": {"node_count": len(nodes), "edge_count": len(edges)}
                    }
            except Exception as e:
                print(f"Neo4j get_graph failed: {e}")
                self.use_neo4j = False
        
        # Memory fallback
        if self.memory_graph is not None:
            import networkx as nx
            nodes = []
            edges = []
            
            # Apply limit
            node_list = list(self.memory_graph.nodes(data=True))[:limit]
            node_ids = set([n[0] for n in node_list])
            
            for node_id, data in node_list:
                # Filter by type if needed
                if filters.get('node_type') and data.get('label') != filters['node_type']:
                    continue
                nodes.append({
                    "id": node_id,
                    "label": data.get('name', data.get('phone_number', data.get('registration_number', node_id))),
                    "type": data.get('label', 'Unknown'),
                    "properties": data
                })
            
            for u, v, data in self.memory_graph.edges(data=True):
                if u in node_ids and v in node_ids:
                    if filters.get('relationship_type') and data.get('type') != filters['relationship_type']:
                        continue
                    edges.append({
                        "id": f"{u}_{v}_{len(edges)}",
                        "source": u,
                        "target": v,
                        "type": data.get('type', 'RELATED'),
                        "properties": data
                    })
            
            return {
                "nodes": nodes,
                "edges": edges[:limit],
                "stats": {"node_count": len(nodes), "edge_count": len(edges)}
            }
        
        return {"nodes": [], "edges": [], "stats": {"node_count": 0, "edge_count": 0}}
    
    def shortest_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """Find shortest path between two nodes"""
        if self.use_neo4j and self.driver:
            try:
                with self.driver.session() as session:
                    query = """
                    MATCH (source {id: $source_id}), (target {id: $target_id}),
                    p = shortestPath((source)-[*]-(target))
                    RETURN p
                    """
                    result = session.run(query, source_id=source_id, target_id=target_id)
                    record = result.single()
                    if record:
                        path = record['p']
                        nodes = []
                        edges = []
                        for i, node in enumerate(path.nodes):
                            nodes.append({
                                "id": node.get('id'),
                                "label": node.get('name', node.get('id')),
                                "type": list(node.labels)[0] if hasattr(node, 'labels') else 'Unknown',
                                "properties": dict(node)
                            })
                        for rel in path.relationships:
                            edges.append({
                                "type": rel.type,
                                "properties": dict(rel)
                            })
                        return {"nodes": nodes, "edges": edges, "length": len(nodes)-1}
            except Exception as e:
                print(f"Neo4j shortest_path failed: {e}")
                self.use_neo4j = False
        
        if self.memory_graph is not None:
            import networkx as nx
            try:
                # Convert to undirected for path finding
                undirected = self.memory_graph.to_undirected()
                path = nx.shortest_path(undirected, source=source_id, target=target_id)
                nodes = []
                for node_id in path:
                    data = self.memory_graph.nodes.get(node_id, {})
                    nodes.append({
                        "id": node_id,
                        "label": data.get('name', data.get('phone_number', node_id)),
                        "type": data.get('label', 'Unknown'),
                        "properties": data
                    })
                edges = []
                for i in range(len(path)-1):
                    edge_data = self.memory_graph.get_edge_data(path[i], path[i+1])
                    if edge_data:
                        # MultiDiGraph returns dict of dicts
                        first_edge = list(edge_data.values())[0] if isinstance(edge_data, dict) else edge_data
                        edges.append({
                            "type": first_edge.get('type', 'RELATED'),
                            "properties": first_edge
                        })
                return {"nodes": nodes, "edges": edges, "length": len(nodes)-1}
            except (nx.NetworkXNoPath, nx.NodeNotFound, Exception) as e:
                print(f"Memory graph shortest_path failed: {e}")
                return {"nodes": [], "edges": [], "length": 0, "error": str(e)}
        
        return {"nodes": [], "edges": [], "length": 0}

# Global instance
graph_client = GraphClient()
