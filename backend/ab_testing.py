import random
from typing import Dict, Any, Optional
import joblib
import os
from logger import logger
from exceptions import ModelLoadError

class ModelWithMetadata:
    def __init__(self, model, version: str, metadata: Dict[str, Any] = None):
        self.model = model
        self.version = version
        self.metadata = metadata or {}

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelWithMetadata] = {}
        self._default_model_id: str = None

    def register_model(self, model_id: str, path: str, version: str):
        """Load and register a model from a file path."""
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Model file not found: {path}")
            
            logger.info(f"Loading model '{model_id}' from {path}")
            model = joblib.load(path)
            self._models[model_id] = ModelWithMetadata(model, version)
            
            if self._default_model_id is None:
                self._default_model_id = model_id
                
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {str(e)}")
            raise ModelLoadError(f"Failed to register model {model_id}: {str(e)}")

    def get_model(self, model_id: str = None) -> ModelWithMetadata:
        """Get a specific model or the default one."""
        if model_id is None:
            model_id = self._default_model_id
        
        if model_id not in self._models:
            raise ValueError(f"Model ID '{model_id}' not found in registry")
            
        return self._models[model_id]

class TrafficRouter:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        # Default config: 100% traffic to default model
        self.routing_weights: Dict[str, float] = {} 

    def set_routing_weights(self, weights: Dict[str, float]):
        """Set traffic distribution weights (e.g. {'v2': 0.8, 'v2_candidate': 0.2})."""
        total = sum(weights.values())
        if abs(total - 1.0) > 0.001:
            logger.warning(f"Routing weights do not sum to 1.0: {total}. Normalizing...")
            # Normalize
            self.routing_weights = {k: v / total for k, v in weights.items()}
        else:
            self.routing_weights = weights
            
        logger.info(f"Traffic routing updated: {self.routing_weights}")

    def select_model(self) -> str:
        """Select a model ID based on configured weights."""
        if not self.routing_weights:
            return self.registry._default_model_id
            
        # Weighted random selection
        models = list(self.routing_weights.keys())
        weights = list(self.routing_weights.values())
        
        selected = random.choices(models, weights=weights, k=1)[0]
        return selected
