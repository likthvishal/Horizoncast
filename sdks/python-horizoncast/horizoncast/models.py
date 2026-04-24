"""HorizonCast Python SDK - Data Models"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Dataset:
    """Dataset metadata."""

    dataset_id: str
    name: str
    row_count: int
    columns: list[str]
    created_at: datetime
    file_key: str


@dataclass
class TrainingRun:
    """Training run status and results."""

    run_id: str
    dataset_id: str
    status: str
    config: Dict[str, Any]
    created_at: datetime
    metrics: Optional[Dict[str, float]] = None
    error: Optional[str] = None


@dataclass
class Prediction:
    """Model prediction with intervals."""

    value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence: Optional[float] = None

    @property
    def interval_width(self) -> Optional[float]:
        if self.lower_bound is not None and self.upper_bound is not None:
            return self.upper_bound - self.lower_bound
        return None
