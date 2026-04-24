"""Pydantic configuration schemas for HorizonCast pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field


class FeatureConfig(BaseModel):
    """Feature engineering configuration."""

    lags: tuple[int, ...] = (7, 14, 28)
    rolling_windows: tuple[int, ...] = (7, 14, 28)
    include_calendar: bool = True
    include_price: bool = True
    include_embeddings: bool = False
    pca_components: int = 8


class ModelConfig(BaseModel):
    """ML model configuration."""

    model_type: Literal["lightgbm", "prophet"] = "lightgbm"
    objective: str = "tweedie"
    tweedie_variance_power: float = 1.1
    metric: str = "rmse"
    num_leaves: int = 127
    learning_rate: float = 0.05
    min_child_samples: int = 20
    colsample_bytree: float = 0.8
    n_estimators: int = 1000
    early_stopping_rounds: int = 50
    random_state: int = 42


class UncertaintyConfig(BaseModel):
    """Uncertainty quantification configuration."""

    method: Literal["conformal"] = "conformal"
    alpha: float = 0.1
    calibration_size: float = 0.2


class EvaluationConfig(BaseModel):
    """Evaluation metrics configuration."""

    holding_cost: float = 0.1
    stockout_cost: float = 0.5
    compute_wrmsse: bool = False


class PipelineConfig(BaseModel):
    """Complete pipeline configuration."""

    features: FeatureConfig = Field(default_factory=FeatureConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    uncertainty: UncertaintyConfig = Field(default_factory=UncertaintyConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    train_lookback_days: int = 365
    max_series: int | None = None
    export_shap: bool = True
    shap_sample_rows: int = 5000

    class Config:
        frozen = True


@dataclass(frozen=True)
class TrainRunMetadata:
    """Metadata about a training run."""

    run_id: str
    config: PipelineConfig
    train_rows: int
    val_rows: int
    test_rows: int
    feature_count: int
    training_time_seconds: float
