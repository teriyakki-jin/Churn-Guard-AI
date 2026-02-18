import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ab_testing import TrafficRouter, ModelRegistry, ModelWithMetadata
from collections import Counter
from services_v2 import ChurnServiceV2
from unittest.mock import MagicMock, patch

def test_router_distribution():
    """Test that traffic router distributes calls according to weights."""
    registry = ModelRegistry()
    registry._default_model_id = "v2"
    
    router = TrafficRouter(registry)
    router.set_routing_weights({"v2": 0.8, "v2_candidate": 0.2})
    
    # Simulate 1000 calls
    selections = [router.select_model() for _ in range(1000)]
    counts = Counter(selections)
    
    # Check v2 traffic (should be around 800)
    v2_count = counts.get("v2", 0)
    candidate_count = counts.get("v2_candidate", 0)
    
    print(f"Distribution: v2={v2_count}, candidate={candidate_count}")
    
    # Allow 5% margin of error
    assert 750 <= v2_count <= 850
    assert 150 <= candidate_count <= 250

def test_service_integration():
    """Test that ChurnServiceV2 initializes registry and loads models."""
    # Ensure candidate model exists (created via copy command previously)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate_path = os.path.join(base_dir, 'churn_model_candidate.pkl')
    
    assert os.path.exists(candidate_path), "Candidate model file must exist for this test"
    
    service = ChurnServiceV2()
    
    # Check if models are registered
    assert 'v2' in service.registry._models
    assert 'v2_candidate' in service.registry._models
    
    # Check router weights
    weights = service.router.routing_weights
    assert weights['v2'] == 0.8
    assert weights['v2_candidate'] == 0.2

def test_predict_returns_version():
    """Test that predict returns the version of the selected model."""
    service = ChurnServiceV2()
    
    # Force router to always select 'v2_candidate'
    service.router.set_routing_weights({"v2_candidate": 1.0})
    
    dummy_input = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "No",
        "MultipleLines": "No phone service",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 29.85,
        "TotalCharges": 29.85
    }
    
    result = service.predict(dummy_input)
    assert result['model_version'] == 'v2_candidate'
