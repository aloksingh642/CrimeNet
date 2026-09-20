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
            return {
                "degree": [],
                "betweenness": [],
                "pagerank": [],
                "closeness": [],
                "density": 0,
                "components": 0,
            }

        degree = nx.degree_centrality(G)
        betweenness = nx.betweenness_centrality(G)
        closeness = nx.closeness_centrality(G)

        try:
            pagerank = nx.pagerank(G)
        except Exception:
            pagerank = {node: 0.0 for node in G.nodes()}

        def format_scores(scores):
            result = []

            for node_id, score in sorted(
                scores.items(),
                key=lambda item: item[1],
                reverse=True
            )[:20]:
                node_data = G.nodes.get(node_id, {})

                result.append({
                    "id": node_id,
                    "label": node_data.get("label", node_id),
                    "type": node_data.get("type", "unknown"),
                    "score": float(score),
                    "evidence": "Observed graph relationships",
                    "interpretation": f"Centrality score: {score:.4f}",
                })

            return result

        return {
            "degree": format_scores(degree),
            "betweenness": format_scores(betweenness),
            "pagerank": format_scores(pagerank),
            "closeness": format_scores(closeness),
            "density": nx.density(G),
            "components": nx.number_connected_components(G),
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