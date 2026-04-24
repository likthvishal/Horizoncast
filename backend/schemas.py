"""Request/response models for API endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DatasetCreate(BaseModel):
    """Request to create/upload a dataset."""

    name: str = Field(..., description="Dataset name")
    description: str = Field("", description="Dataset description")
    file_key: str = Field(..., description="S3/Blob key where file was uploaded")
    row_count: int = Field(..., description="Number of rows in dataset")
    columns: list[str] = Field(..., description="Column names")


class DatasetResponse(BaseModel):
    """Dataset metadata response."""

    dataset_id: str
    name: str
    description: str
    row_count: int
    columns: list[str]
    created_at: datetime
    file_key: str


class TrainingConfig(BaseModel):
    """Configuration for a training run."""

    dataset_id: str
    train_end_date: str = Field(default="2015-03-23", description="Training/val split date")
    val_end_date: str = Field(default="2015-04-19", description="Val/test split date")
    holding_cost: float = Field(default=0.1, ge=0)
    stockout_cost: float = Field(default=0.5, ge=0)
    include_embeddings: bool = Field(default=False, description="Include LLM embeddings")


class TrainingRunResponse(BaseModel):
    """Training run status/results response."""

    run_id: str
    dataset_id: str
    status: str = Field(..., description="pending, running, completed, failed")
    config: dict[str, Any]
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metrics: dict[str, float] | None = None
    error: str | None = None


class PredictionRequest(BaseModel):
    """Request for predictions."""

    run_id: str = Field(..., description="ID of completed training run")
    data: dict[str, Any] = Field(..., description="Features for prediction")


class PredictionResponse(BaseModel):
    """Prediction result with optional intervals."""

    prediction: float
    lower_bound: float | None = None
    upper_bound: float | None = None
    confidence: float | None = None


class BulkPredictionRequest(BaseModel):
    """Bulk prediction request."""

    run_id: str
    file_key: str = Field(..., description="S3/Blob key to CSV file with rows")


class ExplainabilityResponse(BaseModel):
    """Model explainability (SHAP values)."""

    feature_importance: dict[str, float]
    top_features: list[tuple[str, float]]
    shap_available: bool
