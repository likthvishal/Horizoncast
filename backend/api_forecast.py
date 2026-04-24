"""API routes for forecasting and predictions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import get_current_tenant
from backend.schemas import (
    ExplainabilityResponse,
    PredictionRequest,
    PredictionResponse,
    TrainingConfig,
    TrainingRunResponse,
)
from backend.jobs import job_queue, JobStatus
from datetime import datetime
from uuid import uuid4

router = APIRouter(prefix="/api/forecasts", tags=["forecasts"])

# Placeholder store (replace with DB)
runs_store: dict[str, TrainingRunResponse] = {}


@router.post("/train", response_model=dict[str, str])
async def start_training(
    config: TrainingConfig,
    tenant_id: str = Depends(get_current_tenant),
) -> dict[str, str]:
    """Start a training job (async)."""
    run_id = str(uuid4())[:8]

    async def train_task():
        """Placeholder training task."""
        import asyncio
        await asyncio.sleep(2)  # Simulate work
        return {"status": "training_simulated"}

    job = await job_queue.submit_task(train_task)

    run = TrainingRunResponse(
        run_id=run_id,
        dataset_id=config.dataset_id,
        status="pending",
        config=config.dict(),
        created_at=datetime.now(),
        job_id=job.job_id,
    )
    runs_store[run_id] = run

    return {"run_id": run_id, "job_id": job.job_id}


@router.get("/runs/{run_id}", response_model=TrainingRunResponse)
async def get_training_run(
    run_id: str,
    tenant_id: str = Depends(get_current_tenant),
) -> TrainingRunResponse:
    """Get training run status."""
    if run_id not in runs_store:
        raise HTTPException(status_code=404, detail="Training run not found")
    return runs_store[run_id]


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    tenant_id: str = Depends(get_current_tenant),
) -> PredictionResponse:
    """Make a prediction using a trained model."""
    run = runs_store.get(request.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Training run not found")

    # Placeholder prediction logic
    return PredictionResponse(
        prediction=10.5,
        lower_bound=8.2,
        upper_bound=13.1,
        confidence=0.9,
    )


@router.get("/runs/{run_id}/explain", response_model=ExplainabilityResponse)
async def get_model_explanation(
    run_id: str,
    tenant_id: str = Depends(get_current_tenant),
) -> ExplainabilityResponse:
    """Get SHAP-based model explanation."""
    run = runs_store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Training run not found")

    # Placeholder explanation
    return ExplainabilityResponse(
        feature_importance={"lag_7": 0.35, "lag_14": 0.25, "price": 0.20},
        top_features=[("lag_7", 0.35), ("lag_14", 0.25), ("price", 0.20)],
        shap_available=False,
    )
