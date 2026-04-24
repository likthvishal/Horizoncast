"""HorizonCast Python SDK - Main Client"""

import time
from pathlib import Path
from typing import Optional, Dict, Any

import requests

from .models import Dataset, TrainingRun, Prediction


class HorizonCastError(Exception):
    """Base exception for HorizonCast SDK."""

    pass


class HorizonCast:
    """HorizonCast Python SDK client."""

    def __init__(self, api_url: str = "http://localhost:8000", api_key: str = "demo-key-12345"):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request."""
        url = f"{self.api_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HorizonCastError(f"API request failed: {e}") from e

    class Datasets:
        """Datasets API."""

        def __init__(self, parent: "HorizonCast"):
            self.parent = parent

        def upload(self, file_path: str, name: str = None, description: str = "") -> Dataset:
            """Upload a dataset."""
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(path, "rb") as f:
                files = {"file": (path.name, f)}
                response = self.parent.session.post(
                    f"{self.parent.api_url}/api/upload/csv",
                    files=files,
                    data={"name": name or path.stem, "description": description},
                    headers={"Authorization": f"Bearer {self.parent.api_key}"},
                )

            result = response.json()
            return Dataset(
                dataset_id=result.get("dataset_id", ""),
                name=name or path.stem,
                row_count=result.get("row_count", 0),
                columns=result.get("columns", []),
                created_at=None,
                file_key=result.get("file_key", ""),
            )

        def list(self) -> list[Dataset]:
            """List all datasets."""
            result = self.parent._request("GET", "/api/datasets/")
            return [
                Dataset(
                    dataset_id=d["dataset_id"],
                    name=d["name"],
                    row_count=d["row_count"],
                    columns=d["columns"],
                    created_at=d["created_at"],
                    file_key=d["file_key"],
                )
                for d in result
            ]

    class Forecasts:
        """Forecasting API."""

        def __init__(self, parent: "HorizonCast"):
            self.parent = parent

        def train(
            self,
            dataset_id: str,
            train_end_date: str = "2025-01-01",
            val_end_date: str = "2025-02-01",
            **kwargs,
        ) -> TrainingRun:
            """Start training a model."""
            config = {
                "dataset_id": dataset_id,
                "train_end_date": train_end_date,
                "val_end_date": val_end_date,
                **kwargs,
            }
            result = self.parent._request("POST", "/api/forecasts/train", json=config)
            return TrainingRun(
                run_id=result["run_id"],
                dataset_id=dataset_id,
                status="pending",
                config=config,
                created_at=None,
            )

        def get(self, run_id: str) -> TrainingRun:
            """Get training run status."""
            result = self.parent._request("GET", f"/api/forecasts/runs/{run_id}")
            return TrainingRun(
                run_id=result["run_id"],
                dataset_id=result["dataset_id"],
                status=result["status"],
                config=result.get("config", {}),
                created_at=result.get("created_at"),
                metrics=result.get("metrics"),
                error=result.get("error"),
            )

        def wait(self, run_id: str, timeout: int = 3600, poll_interval: int = 5) -> TrainingRun:
            """Wait for training to complete."""
            start_time = time.time()
            while time.time() - start_time < timeout:
                run = self.get(run_id)
                if run.status in ["completed", "failed"]:
                    return run
                time.sleep(poll_interval)
            raise HorizonCastError(f"Training run {run_id} timeout after {timeout}s")

        def predict(self, run_id: str, data: Dict[str, float]) -> Prediction:
            """Make a prediction."""
            request_data = {"run_id": run_id, "data": data}
            result = self.parent._request("POST", "/api/forecasts/predict", json=request_data)
            return Prediction(
                value=result["prediction"],
                lower_bound=result.get("lower_bound"),
                upper_bound=result.get("upper_bound"),
                confidence=result.get("confidence"),
            )

        def explain(self, run_id: str) -> Dict[str, Any]:
            """Get model explanation."""
            return self.parent._request("GET", f"/api/forecasts/runs/{run_id}/explain")

    def __init__(self, api_url: str = "http://localhost:8000", api_key: str = "demo-key-12345"):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

        self.datasets = self.Datasets(self)
        self.forecasts = self.Forecasts(self)
