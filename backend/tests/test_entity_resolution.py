import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ai.entity_resolution import entity_resolver

def test_name_similarity():
    assert entity_resolver.name_similarity("Rahul Sharma", "Rahul Sharma") == 1.0
    assert entity_resolver.name_similarity("Rahul Sharma", "R. Sharma") > 0.6
    assert entity_resolver.name_similarity("Amit Verma", "Rahul Sharma") < 0.5

def test_duplicate_detection():
    persons = [
        {"id": 1, "name": "Rahul Sharma", "phone": "9876543210"},
        {"id": 2, "name": "R. Sharma", "phone": "9876543210"},
        {"id": 3, "name": "Amit Verma", "phone": "9123456789"},
    ]
    dups = entity_resolver.find_duplicates(persons)
    assert len(dups) >= 1
    assert dups[0]["entity1_id"] in [1,2]

if __name__ == "__main__":
    test_name_similarity()
    test_duplicate_detection()
    print("Entity resolution tests passed")
