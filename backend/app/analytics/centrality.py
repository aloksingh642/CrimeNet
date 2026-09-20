from typing import Any, Dict

import networkx as nx


class AnalyticsService:
    def build_nx_graph(self, graph_data: Dict[str, Any]) -> nx.Graph:
        G = nx.Graph()

        for node in graph_data.get("nodes", []):
            node_data = dict(node.get("properties", {}))
            node_data["label"] = node.get("label")
            node_data["type"] = node.get("type")

            G.add_node(node["id"], **node_data)

        for edge in graph_data.get("edges", []):
            edge_data = dict(edge.get("properties", {}))
            edge_data["type"] = edge.get("type")

            G.add_edge(
                edge["source"],
                edge["target"],
                **edge_data
            )

        return G

    def calculate_centrality(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        G = self.build_nx_graph(graph_data)

        if G.number_of_nodes() == 0:
            return {}

        degree = nx.degree_centrality(G)

        betweenness = nx.betweenness_centrality(G)

        closeness = nx.closeness_centrality(G)

        return {
            "degree": degree,
            "betweenness": betweenness,
            "closeness": closeness,
        }

    def detect_communities(self, graph_data: Dict[str, Any]) -> Dict[str, int]:
        G = self.build_nx_graph(graph_data)

        if G.number_of_nodes() == 0:
            return {}

        if G.number_of_edges() == 0:
            return {
                node: index
                for index, node in enumerate(G.nodes())
            }

        communities = nx.community.greedy_modularity_communities(G)

        result = {}

        for community_id, community in enumerate(communities):
            for node in community:
                result[node] = community_id

        return result


analytics_service = AnalyticsService()
