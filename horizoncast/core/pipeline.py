"""Main ForecastingService orchestration for the ML pipeline."""

from __future__ import annotations

import io
import pickle
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from rich.console import Console

from horizoncast.core.artifacts import ArtifactStore, ModelArtifact
from horizoncast.core.config import PipelineConfig
from horizoncast.evaluation.business_cost import inventory_cost
from horizoncast.evaluation.metrics import coverage, interval_width, mae, pinball_loss, rmse
from horizoncast.features.classical import (
    CategoricalEncoders,
    add_calendar_features,
    add_lag_rolling_features,
    add_price_features,
    fit_categorical_encoders,
)
from horizoncast.models.conformal import ConformalConfig, MAPIEConformalRegressor
from horizoncast.models.forecaster import LightGBMForecaster, LightGBMForecasterConfig

console = Console()


class ForecastingService:
    """Unified forecasting service for HorizonCast.
    
    Handles:
    - Feature engineering
    - Model training
    - Prediction with uncertainty
    - Evaluation
    - Artifact versioning
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.config = config or PipelineConfig()
        self.artifact_store = artifact_store
        self.run_id = str(uuid.uuid4())[:8]

        self.forecaster: LightGBMForecaster | None = None
        self.conformal: MAPIEConformalRegressor | None = None
        self.encoders: CategoricalEncoders | None = None
        self.feature_columns: list[str] = []

    def _prepare_features(
        self,
        df: pd.DataFrame,
        target_col: str = "sales",
        fit_encoders: bool = False,
    ) -> pd.DataFrame:
        """Prepare engineered features."""
        features_df = df.copy()

        if self.config.features.include_calendar:
            features_df = add_calendar_features(features_df)

        if self.config.features.include_price:
            features_df = add_price_features(features_df)

        features_df = add_lag_rolling_features(
            features_df,
            cfg=self.config.features,
        )

        categorical_cols = ["item_id", "dept_id", "store_id", "state_id", "cat_id"]
        existing_cats = [c for c in categorical_cols if c in features_df.columns]

        if fit_encoders:
            self.encoders = fit_categorical_encoders(features_df[existing_cats])

        if self.encoders is not None:
            for col in existing_cats:
                if col in features_df.columns:
                    try:
                        features_df[col] = self.encoders.__getattribute__(col.replace("_id", "")).transform(
                            features_df[col].astype(str)
                        )
                    except Exception:
                        pass

        return features_df

    def train(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        target_col: str = "sales",
        date_col: str = "date",
    ) -> dict[str, Any]:
        """Train the forecasting model.
        
        Returns:
            Dictionary with training metrics and metadata.
        """
        console.log("[bold]Starting training...[/bold]")
        start_time = time.time()

        X_train = self._prepare_features(train_df, target_col=target_col, fit_encoders=True)
        X_val = self._prepare_features(val_df, target_col=target_col, fit_encoders=False)

        feature_cols = [
            c for c in X_train.columns
            if c not in [target_col, date_col, "id", "item_id", "dept_id", "store_id", "state_id", "cat_id"]
            and X_train[c].dtype in [np.float32, np.float64, int, np.int32, np.int64]
        ]

        self.feature_columns = feature_cols
        console.log(f"Using {len(feature_cols)} features")

        X_train_feat = X_train[feature_cols].fillna(0)
        y_train = train_df[target_col].to_numpy(dtype=np.float32)

        X_val_feat = X_val[feature_cols].fillna(0)
        y_val = val_df[target_col].to_numpy(dtype=np.float32)

        lgbm_cfg = LightGBMForecasterConfig(
            objective=self.config.model.objective,
            tweedie_variance_power=self.config.model.tweedie_variance_power,
            metric=self.config.model.metric,
            num_leaves=self.config.model.num_leaves,
            learning_rate=self.config.model.learning_rate,
            min_child_samples=self.config.model.min_child_samples,
            colsample_bytree=self.config.model.colsample_bytree,
            n_estimators=self.config.model.n_estimators,
            early_stopping_rounds=self.config.model.early_stopping_rounds,
            random_state=self.config.model.random_state,
        )

        self.forecaster = LightGBMForecaster(cfg=lgbm_cfg)
        self.forecaster.fit(X_train_feat, y_train, X_val_feat, y_val)

        y_pred = self.forecaster.predict(X_val_feat)

        val_rmse = rmse(y_val, y_pred)
        val_mae = mae(y_val, y_pred)

        console.log(f"[green]✓ Training complete in {time.time() - start_time:.1f}s[/green]")
        console.log(f"  Val RMSE: {val_rmse:.4f}")
        console.log(f"  Val MAE: {val_mae:.4f}")

        return {
            "val_rmse": val_rmse,
            "val_mae": val_mae,
            "train_rows": len(train_df),
            "val_rows": len(val_df),
            "feature_count": len(feature_cols),
            "training_time_seconds": time.time() - start_time,
        }

    def predict(
        self,
        test_df: pd.DataFrame,
        return_intervals: bool = True,
        target_col: str = "sales",
        date_col: str = "date",
    ) -> tuple[pd.DataFrame, np.ndarray | None]:
        """Make predictions with optional uncertainty intervals.
        
        Returns:
            (predictions_df, intervals_array)
        """
        if self.forecaster is None:
            raise RuntimeError("Model not trained. Call train() first.")

        X_test = self._prepare_features(test_df, target_col=target_col, fit_encoders=False)
        X_test_feat = X_test[self.feature_columns].fillna(0)

        y_pred = self.forecaster.predict(X_test_feat)

        results = test_df[[date_col]].copy() if date_col in test_df.columns else pd.DataFrame()
        results["prediction"] = y_pred

        intervals = None
        if return_intervals and self.forecaster.model is not None:
            conformal_cfg = ConformalConfig(alpha=self.config.uncertainty.alpha)
            self.conformal = MAPIEConformalRegressor(cfg=conformal_cfg)

            calib_size = int(len(X_test_feat) * self.config.uncertainty.calibration_size)
            X_calib = X_test_feat[:calib_size]
            y_calib = y_pred[:calib_size]

            X_test_intervals = X_test_feat[calib_size:]

            try:
                self.conformal.fit(self.forecaster.model, X_calib, y_calib)
                y_pred_intervals, intervals = self.conformal.predict(X_test_intervals)
                results = results.iloc[calib_size:].reset_index(drop=True)
                results["lower"] = intervals[:, 0] if intervals.ndim > 1 else intervals[0]
                results["upper"] = intervals[:, 1] if intervals.ndim > 1 else intervals[1]
            except Exception as e:
                console.log(f"[yellow]Warning: Conformal intervals failed: {e}[/yellow]")

        return results, intervals

    def evaluate(
        self,
        test_df: pd.DataFrame,
        target_col: str = "sales",
        date_col: str = "date",
    ) -> dict[str, float]:
        """Evaluate model on test set.
        
        Returns:
            Dictionary with evaluation metrics.
        """
        if self.forecaster is None:
            raise RuntimeError("Model not trained. Call train() first.")

        results_df, intervals = self.predict(
            test_df,
            return_intervals=True,
            target_col=target_col,
            date_col=date_col,
        )

        if len(results_df) == 0:
            console.log("[yellow]Warning: No test predictions[/yellow]")
            return {}

        y_test = test_df[target_col].iloc[-len(results_df):].to_numpy(dtype=np.float32)
        y_pred = results_df["prediction"].to_numpy(dtype=np.float32)

        metrics = {
            "test_rmse": rmse(y_test, y_pred),
            "test_mae": mae(y_test, y_pred),
        }

        if "lower" in results_df.columns and "upper" in results_df.columns:
            y_lower = results_df["lower"].to_numpy()
            y_upper = results_df["upper"].to_numpy()

            metrics["test_coverage"] = coverage(y_test, y_lower, y_upper)
            metrics["test_interval_width"] = interval_width(y_lower, y_upper)
            metrics["test_pinball_loss"] = pinball_loss(
                y_test, y_lower, y_upper,
                q_lower=(1.0 - self.config.uncertainty.alpha) / 2,
                q_upper=0.5 + (1.0 - self.config.uncertainty.alpha) / 2,
            )

            holding_cost = self.config.evaluation.holding_cost
            stockout_cost = self.config.evaluation.stockout_cost
            metrics["test_business_cost"] = inventory_cost(
                y_test, y_pred, holding_cost, stockout_cost
            )

        console.log("[green]Evaluation metrics:[/green]")
        for k, v in metrics.items():
            console.log(f"  {k}: {v:.4f}")

        return metrics

    def save_artifact(self, metrics: dict[str, float] | None = None) -> str:
        """Save trained model as a versioned artifact."""
        if self.forecaster is None or self.forecaster.model is None:
            raise RuntimeError("No trained model to save")

        if self.artifact_store is None:
            raise RuntimeError("No artifact store configured")

        model_bytes = io.BytesIO()
        pickle.dump(self.forecaster.model, model_bytes)
        model_bytes.seek(0)

        artifact = ModelArtifact(
            version=self.run_id,
            created_at=datetime.now(),
            config_dict=self.config.dict(),
            metrics=metrics or {},
            feature_columns=self.feature_columns,
            training_metadata={
                "run_id": self.run_id,
                "forecaster_type": "LightGBM",
            },
        )

        version_id = self.artifact_store.save_artifact(artifact, model_bytes.getvalue())
        console.log(f"[green]✓ Model saved as version {version_id}[/green]")
        return version_id

    def load_artifact(self, version_id: str) -> None:
        """Load a saved artifact."""
        if self.artifact_store is None:
            raise RuntimeError("No artifact store configured")

        artifact, model_bytes = self.artifact_store.load_artifact(version_id)
        self.config = PipelineConfig(**artifact.config_dict)
        self.feature_columns = artifact.feature_columns

        if model_bytes is not None:
            model_obj = pickle.loads(model_bytes)
            self.forecaster = LightGBMForecaster()
            self.forecaster.model = model_obj

        console.log(f"[green]✓ Loaded artifact version {version_id}[/green]")
