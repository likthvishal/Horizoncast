"""Model artifact versioning and storage management."""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class ModelArtifact:
    """Versioned model artifact with metadata."""

    version: str
    created_at: datetime
    config_dict: dict[str, Any]
    model_object: Any = None
    metrics: dict[str, float] = field(default_factory=dict)
    feature_columns: list[str] = field(default_factory=list)
    shap_values: np.ndarray | None = None
    training_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (excluding model object)."""
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "config": self.config_dict,
            "metrics": self.metrics,
            "feature_columns": self.feature_columns,
            "training_metadata": self.training_metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelArtifact:
        """Deserialize from dictionary."""
        return cls(
            version=data["version"],
            created_at=datetime.fromisoformat(data["created_at"]),
            config_dict=data["config"],
            metrics=data.get("metrics", {}),
            feature_columns=data.get("feature_columns", []),
            training_metadata=data.get("training_metadata", {}),
        )


class ArtifactStore:
    """Manages versioned model artifacts."""

    def __init__(self, store_dir: Path) -> None:
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.store_dir / "manifest.json"

    def _get_manifest(self) -> dict[str, Any]:
        """Load or initialize manifest."""
        if self.manifest_file.exists():
            with open(self.manifest_file, "r") as f:
                return json.load(f)
        return {"artifacts": [], "current_version": None}

    def _save_manifest(self, manifest: dict[str, Any]) -> None:
        """Save manifest."""
        with open(self.manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

    def save_artifact(
        self,
        artifact: ModelArtifact,
        model_bytes: bytes | None = None,
    ) -> str:
        """Save an artifact version and return the version ID."""
        manifest = self._get_manifest()

        version_dir = self.store_dir / artifact.version
        version_dir.mkdir(parents=True, exist_ok=True)

        metadata_path = version_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(artifact.to_dict(), f, indent=2)

        if model_bytes is not None:
            model_path = version_dir / "model.pkl"
            with open(model_path, "wb") as f:
                f.write(model_bytes)

        if artifact.shap_values is not None:
            shap_path = version_dir / "shap_values.npy"
            np.save(shap_path, artifact.shap_values)

        manifest["artifacts"].append({
            "version": artifact.version,
            "created_at": artifact.created_at.isoformat(),
            "metrics": artifact.metrics,
        })
        manifest["current_version"] = artifact.version

        self._save_manifest(manifest)
        return artifact.version

    def load_artifact(self, version: str) -> tuple[ModelArtifact, bytes | None]:
        """Load an artifact and return (artifact, model_bytes)."""
        version_dir = self.store_dir / version
        if not version_dir.exists():
            raise ValueError(f"Artifact version {version} not found")

        metadata_path = version_dir / "metadata.json"
        with open(metadata_path, "r") as f:
            data = json.load(f)

        artifact = ModelArtifact.from_dict(data)

        model_bytes = None
        model_path = version_dir / "model.pkl"
        if model_path.exists():
            with open(model_path, "rb") as f:
                model_bytes = f.read()

        shap_path = version_dir / "shap_values.npy"
        if shap_path.exists():
            artifact.shap_values = np.load(shap_path)

        return artifact, model_bytes

    def load_current(self) -> tuple[ModelArtifact, bytes | None]:
        """Load the current/latest artifact."""
        manifest = self._get_manifest()
        current_version = manifest.get("current_version")
        if current_version is None:
            raise ValueError("No current artifact version set")
        return self.load_artifact(current_version)

    def list_artifacts(self) -> list[dict[str, Any]]:
        """List all saved artifacts."""
        manifest = self._get_manifest()
        return manifest.get("artifacts", [])
