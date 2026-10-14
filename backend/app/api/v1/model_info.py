"""
Model Information and Benchmark Metrics Endpoints.
"""
import os
import json
from fastapi import APIRouter
from backend.app.schemas import ModelInfoResponse
from backend.app.ml.model import default_model_service, ARTIFACTS_DIR

router = APIRouter()


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Get ML Model Metadata & Dataset Provenance",
    description="Returns verified performance metrics, feature importances, and dataset citations."
)
async def get_model_info():
    info = default_model_service.get_info()
    return ModelInfoResponse(
        model_version=info["model_version"],
        architecture=info["architecture"],
        is_loaded=info["is_loaded"],
        training_dataset=info["training_dataset"],
        dataset_provenance=info["dataset_provenance"],
        metrics=info["metrics"],
        top_features=info["top_features"]
    )


@router.get(
    "/benchmark",
    summary="Get Comparative Research Benchmark",
    description="Returns comparative evaluation across Rule Baseline, ML, Hybrid, and Two-Stage Selective Architecture."
)
async def get_benchmark():
    benchmark_file = os.path.join(ARTIFACTS_DIR, "evaluation_benchmark.json")
    if os.path.exists(benchmark_file):
        with open(benchmark_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "status": "pending",
        "message": "Benchmark not yet computed. Run ml/evaluate.py to generate benchmark."
    }
