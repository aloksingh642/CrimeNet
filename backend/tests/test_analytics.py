import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.analytics.centrality import analytics_service

def test_centrality():
    graph_data = {
        "nodes": [
            {"id": "person_1", "label": "A", "type": "Person", "properties": {}},
            {"id": "person_2", "label": "B", "type": "Person", "properties": {}},
            {"id": "person_3", "label": "C", "type": "Person", "properties": {}},
        ],
        "edges": [
            {"id": "e1", "source": "person_1", "target": "person_2", "type": "ASSOCIATED_WITH", "properties": {}},
            {"id": "e2", "source": "person_2", "target": "person_3", "type": "ASSOCIATED_WITH", "properties": {}},
        ]
    }
    result = analytics_service.calculate_centrality(graph_data)
    assert "degree" in result
    assert "betweenness" in result
    assert result["density"] >= 0

def test_communities():
    graph_data = {
        "nodes": [
            {"id": "person_1", "label": "A", "type": "Person", "properties": {}},
            {"id": "person_2", "label": "B", "type": "Person", "properties": {}},
            {"id": "person_3", "label": "C", "type": "Person", "properties": {}},
            {"id": "person_4", "label": "D", "type": "Person", "properties": {}},
        ],
        "edges": [
            {"id": "e1", "source": "person_1", "target": "person_2", "type": "ASSOCIATED_WITH", "properties": {}},
            {"id": "e2", "source": "person_3", "target": "person_4", "type": "ASSOCIATED_WITH", "properties": {}},
        ]
    }
    comms = analytics_service.detect_communities(graph_data)
    assert len(comms) >= 1

if __name__ == "__main__":
    test_centrality()
    test_communities()
    print("Analytics tests passed")
