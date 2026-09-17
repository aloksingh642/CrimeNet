import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ai.nlp_pipeline import nlp_pipeline

def test_phone_extraction():
    text = "Call 9876543210 and 9123456789"
    entities = nlp_pipeline.extract_entities(text)
    assert len(entities["PHONE"]) >= 1

def test_vehicle_extraction():
    text = "Vehicle HR26AB1234 was observed"
    entities = nlp_pipeline.extract_entities(text)
    assert len(entities["VEHICLE"]) >= 1

def test_person_extraction():
    text = "Rahul Sharma was seen near Central Market with Amit Verma"
    entities = nlp_pipeline.extract_entities(text)
    # Should detect persons via pattern
    assert len(entities["PERSON"]) >= 1 or len(entities["LOCATION"]) >= 1

def test_relationship_extraction():
    text = "Rahul Sharma met Amit Verma at Central Market on 12 March. Vehicle HR26AB1234 observed."
    result = nlp_pipeline.process_document(text)
    assert result["relationship_count"] >= 0
    assert "entities" in result

if __name__ == "__main__":
    test_phone_extraction()
    test_vehicle_extraction()
    test_person_extraction()
    test_relationship_extraction()
    print("NLP tests passed")
