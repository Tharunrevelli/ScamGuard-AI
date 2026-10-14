"""
Model Loader and Inference Service.
Manages the scikit-learn pipeline lifecycle, probability calibration, and feature explanations.
"""
import os
import json
import joblib
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.joblib")
METRICS_PATH = os.path.join(ARTIFACTS_DIR, "metrics.json")
FEATURES_PATH = os.path.join(ARTIFACTS_DIR, "feature_weights.json")


class ModelService:
    """Singleton service for loading and serving ML predictions."""

    def __init__(self):
        self.pipeline = None
        self.metrics = {}
        self.feature_weights = {}
        self.model_version = "v1.0.0-tfidf-calibrated-logreg"
        self.is_loaded = False
        self._load()

    def _load(self):
        """Load trained pipeline and metadata artifacts."""
        if os.path.exists(MODEL_PATH):
            try:
                self.pipeline = joblib.load(MODEL_PATH)
                self.is_loaded = True
            except Exception as e:
                print(f"[ModelService] Error loading model from {MODEL_PATH}: {e}")
                self.is_loaded = False
        else:
            print(f"[ModelService] Warning: Model artifact not found at {MODEL_PATH}")
            self.is_loaded = False

        if os.path.exists(METRICS_PATH):
            try:
                with open(METRICS_PATH, "r", encoding="utf-8") as f:
                    self.metrics = json.load(f)
            except Exception as e:
                print(f"[ModelService] Error loading metrics: {e}")

        if os.path.exists(FEATURES_PATH):
            try:
                with open(FEATURES_PATH, "r", encoding="utf-8") as f:
                    self.feature_weights = json.load(f)
            except Exception as e:
                print(f"[ModelService] Error loading feature weights: {e}")

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Run inference on input text.
        Returns probability of scam (0.0 to 1.0) and status.
        """
        if not text or not text.strip():
            return {
                "scam_probability": 0.0,
                "predicted_label": 0,
                "label_name": "ham",
                "model_version": self.model_version,
                "model_available": self.is_loaded,
            }

        if not self.is_loaded or self.pipeline is None:
            # Fallback heuristic probability if model artifact is unavailable
            return {
                "scam_probability": 0.50,
                "predicted_label": 0,
                "label_name": "unavailable",
                "model_version": f"{self.model_version}-fallback",
                "model_available": False,
            }

        try:
            probabilities = self.pipeline.predict_proba([text])[0]
            # probabilities[0] = ham, probabilities[1] = spam/scam
            scam_prob = float(probabilities[1])
            predicted_label = 1 if scam_prob >= 0.50 else 0

            return {
                "scam_probability": round(scam_prob, 4),
                "predicted_label": predicted_label,
                "label_name": "spam" if predicted_label == 1 else "ham",
                "model_version": self.model_version,
                "model_available": True,
            }
        except Exception as e:
            print(f"[ModelService] Prediction failure: {e}")
            return {
                "scam_probability": 0.50,
                "predicted_label": 0,
                "label_name": "error",
                "model_version": f"{self.model_version}-error",
                "model_available": False,
            }

    def get_info(self) -> Dict[str, Any]:
        """Return model metadata, dataset provenance, and performance benchmark."""
        return {
            "model_version": self.model_version,
            "architecture": "N-gram TF-IDF (1,2) + Calibrated Logistic Regression (Sigmoid / 5-Fold CV)",
            "is_loaded": self.is_loaded,
            "training_dataset": "SMS Spam Collection v.1 (UCI Machine Learning Repository)",
            "dataset_provenance": "Almeida et al. (2011), ACM DocEng. 5,574 genuine labeled SMS messages.",
            "metrics": self.metrics,
            "top_features": {
                "spam_signals": self.feature_weights.get("top_spam_indicators", [])[:10],
                "ham_signals": self.feature_weights.get("top_ham_indicators", [])[:10],
            }
        }


# Global singleton service
default_model_service = ModelService()
