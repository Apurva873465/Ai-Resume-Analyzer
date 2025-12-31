import pickle
import os
from typing import Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Singleton class to load and manage ML models for resume analysis.
    Ensures models are loaded once at startup and are thread-safe.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.model = None
            self.vectorizer = None
            self.label_encoder = None
            self._load_models()
            ModelLoader._initialized = True
    
    def _load_models(self) -> None:
        """
        Load all required models from the models directory.
        """
        try:
            # Define model paths
            model_path = os.path.join('models', 'model.pkl')
            vectorizer_path = os.path.join('models', 'vectorizer.pkl')
            label_encoder_path = os.path.join('models', 'label_encoder.pkl')
            
            # Load the trained model
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("Model loaded successfully")
            
            # Load the vectorizer
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            logger.info("Vectorizer loaded successfully")
            
            # Load the label encoder
            with open(label_encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            logger.info("Label encoder loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def get_model(self) -> Any:
        """Return the loaded ML model."""
        return self.model
    
    def get_vectorizer(self) -> Any:
        """Return the loaded vectorizer."""
        return self.vectorizer
    
    def get_label_encoder(self) -> Any:
        """Return the loaded label encoder."""
        return self.label_encoder
    
    def is_loaded(self) -> bool:
        """Check if all models are loaded."""
        return all([
            self.model is not None,
            self.vectorizer is not None,
            self.label_encoder is not None
        ])


# Global instance to ensure models are loaded once
model_loader = ModelLoader()