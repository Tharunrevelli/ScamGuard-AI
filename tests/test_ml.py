"""
Tests for ML Model Inference, Probability Calibration, and Metadata Loading.
"""
import pytest
from backend.app.ml.model import default_model_service


def test_model_is_loaded():
    assert default_model_service.is_loaded is True
    assert default_model_service.pipeline is not None


def test_model_predict_empty_text():
    res = default_model_service.predict("")
    assert res["scam_probability"] == 0.0
    assert res["predicted_label"] == 0


def test_model_predict_scam_sample():
    text = "FREE ENTRY in 2 a weekly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entry question"
    res = default_model_service.predict(text)
    assert res["scam_probability"] > 0.50
    assert res["predicted_label"] == 1
    assert res["label_name"] == "spam"


def test_model_predict_ham_sample():
    text = "Hey what time are you coming over tonight for dinner?"
    res = default_model_service.predict(text)
    assert res["scam_probability"] < 0.30
    assert res["predicted_label"] == 0
    assert res["label_name"] == "ham"


def test_model_info_structure():
    info = default_model_service.get_info()
    assert "metrics" in info
    assert "accuracy" in info["metrics"]
    assert "top_features" in info
