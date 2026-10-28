"""
Model Loader and Inference Service.
Manages the scikit-learn pipeline lifecycle, probability calibration, and feature explanations.
"""
import os
import json
import joblib
from typing import Dict, Any, Optional, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.joblib")
METRICS_PATH = os.path.join(ARTIFACTS_DIR, "metrics.json")
FEATURES_PATH = os.path.join(ARTIFACTS_DIR, "feature_weights.json")
ENSEMBLE_PATH = os.path.join(ARTIFACTS_DIR, "ensemble_breakdown.json")


class ModelService:
    """Singleton service for loading and serving ML predictions."""

    def __init__(self):
        self.pipeline = None
        self.metrics = {}
        self.feature_weights = {}
        self.ensemble_info = {}
        self.model_version = "v2.0.0-calibrated-soft-voting-ensemble"
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

        if os.path.exists(ENSEMBLE_PATH):
            try:
                with open(ENSEMBLE_PATH, "r", encoding="utf-8") as f:
                    self.ensemble_info = json.load(f)
            except Exception as e:
                print(f"[ModelService] Error loading ensemble info: {e}")

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
                "token_attributions": []
            }

        if not self.is_loaded or self.pipeline is None:
            # Fallback heuristic probability if model artifact is unavailable
            return {
                "scam_probability": 0.50,
                "predicted_label": 0,
                "label_name": "unavailable",
                "model_version": f"{self.model_version}-fallback",
                "model_available": False,
                "token_attributions": []
            }

        try:
            probabilities = self.pipeline.predict_proba([text])[0]
            # probabilities[0] = ham, probabilities[1] = spam/scam
            scam_prob = float(probabilities[1])
            predicted_label = 1 if scam_prob >= 0.50 else 0

            # Compute token-level explainability attribution
            token_attributions = self._compute_token_attributions(text)

            return {
                "scam_probability": round(scam_prob, 4),
                "predicted_label": predicted_label,
                "label_name": "spam" if predicted_label == 1 else "ham",
                "model_version": self.model_version,
                "model_available": True,
                "token_attributions": token_attributions
            }
        except Exception as e:
            print(f"[ModelService] Prediction failure: {e}")
            return {
                "scam_probability": 0.50,
                "predicted_label": 0,
                "label_name": "error",
                "model_version": f"{self.model_version}-error",
                "model_available": False,
                "token_attributions": []
            }

    def _compute_token_attributions(self, text: str) -> List[Dict[str, Any]]:
        """Identify which words in the text align with top scam or ham features."""
        top_spam = {f["feature"].lower(): f["weight"] for f in self.feature_weights.get("top_spam_indicators", [])}
        top_ham = {f["feature"].lower(): abs(f["weight"]) for f in self.feature_weights.get("top_ham_indicators", [])}

        words = text.lower().split()
        attributions = []

        for w in set(words):
            clean_w = w.strip(".,;:!?()[]\"'")
            if clean_w in top_spam:
                attributions.append({
                    "token": clean_w,
                    "impact": "SCAM_SIGNAL",
                    "weight": round(top_spam[clean_w], 2),
                    "description": f"Statistical scam marker (weight: +{top_spam[clean_w]:.2f})"
                })
            elif clean_w in top_ham:
                attributions.append({
                    "token": clean_w,
                    "impact": "BENIGN_SIGNAL",
                    "weight": round(top_ham[clean_w], 2),
                    "description": f"Interpersonal conversational marker (weight: -{top_ham[clean_w]:.2f})"
                })

        # Sort by weight descending
        attributions = sorted(attributions, key=lambda a: -a["weight"])
        return attributions[:8]

    def get_info(self) -> Dict[str, Any]:
        """Return model metadata, dataset provenance, and performance benchmark."""
        return {
            "model_version": self.model_version,
            "architecture": "Calibrated Soft-Voting Ensemble [Logistic Regression (w=2) + Complement Naive Bayes (w=1) + Random Forest (w=1)] with Multi-Channel Word/Char FeatureUnion",
            "is_loaded": self.is_loaded,
            "training_dataset": "Unified SMS Spam Collection v.1 (UCI) + 2026 Modern Scam Corpus",
            "dataset_provenance": "Almeida et al. (DocEng'11) + Curated 2026 Smishing Vectors (5,619 total messages).",
            "metrics": self.metrics,
            "ensemble_breakdown": self.ensemble_info,
            "top_features": {
                "spam_signals": self.feature_weights.get("top_spam_indicators", [])[:15],
                "ham_signals": self.feature_weights.get("top_ham_indicators", [])[:15],
            }
        }


# Global singleton service
default_model_service = ModelService()
