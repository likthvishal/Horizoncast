from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from rich.console import Console
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit

console = Console()


@dataclass(frozen=True)
class LightGBMForecasterConfig:
    """
    LightGBM wrapper for demand forecasting on count-like targets.

    Uses early stopping on a validation set to prevent overfitting.
    """

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


class LightGBMForecaster:
    """
    Fit a LightGBM regression model with early stopping.

    The forecaster expects tabular feature matrices (already engineered).
    """

    def __init__(self, cfg: LightGBMForecasterConfig | None = None) -> None:
        self.cfg = cfg or LightGBMForecasterConfig()
        self.model = None

    def fit(
        self,
        X_train: pd.DataFrame | np.ndarray,
        y_train: np.ndarray,
        X_val: pd.DataFrame | np.ndarray,
        y_val: np.ndarray,
        **lgbm_fit_kwargs: Any,
    ) -> "LightGBMForecaster":
        try:
            from lightgbm import LGBMRegressor
            from lightgbm import early_stopping, log_evaluation
        except Exception as e:  # pragma: no cover
            raise ImportError("LightGBM is not installed. Please `pip install lightgbm`.") from e

        if self.cfg.objective == "tweedie":
            params = {
                "objective": self.cfg.objective,
                "tweedie_variance_power": self.cfg.tweedie_variance_power,
                "metric": self.cfg.metric,
                "num_leaves": self.cfg.num_leaves,
                "learning_rate": self.cfg.learning_rate,
                "min_child_samples": self.cfg.min_child_samples,
                "colsample_bytree": self.cfg.colsample_bytree,
                "n_estimators": self.cfg.n_estimators,
                "random_state": self.cfg.random_state,
            }
        else:
            params = {
                "objective": self.cfg.objective,
                "metric": self.cfg.metric,
                "num_leaves": self.cfg.num_leaves,
                "learning_rate": self.cfg.learning_rate,
                "min_child_samples": self.cfg.min_child_samples,
                "colsample_bytree": self.cfg.colsample_bytree,
                "n_estimators": self.cfg.n_estimators,
                "random_state": self.cfg.random_state,
            }

        self.model = LGBMRegressor(**params)
        fit_kwargs = {
            "eval_set": [(X_val, y_val)],
            "eval_metric": self.cfg.metric,
            "callbacks": [
                early_stopping(self.cfg.early_stopping_rounds),
                log_evaluation(period=0),
            ],
        }
        fit_kwargs.update(lgbm_fit_kwargs)

        self.model.fit(X_train, y_train, **fit_kwargs)
        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Call fit() before predict().")
        preds = self.model.predict(X)
        return np.asarray(preds, dtype=np.float32)

    def fit_time_series_cv(
        self,
        df: pd.DataFrame,
        feature_cols: list[str],
        target_col: str,
        date_col: str,
        cv_folds: int = 5,
        **lgbm_fit_kwargs: Any,
    ) -> "LightGBMForecaster":
        """
        Time-series CV (folds over unique dates; no shuffle).

        Selects the model that achieves lowest RMSE on the validation slice.
        """
        if date_col not in df.columns:
            raise ValueError(f"date_col {date_col!r} not in df.")

        dates = pd.to_datetime(df[date_col], errors="coerce").dropna().unique()
        dates = np.sort(dates)
        if len(dates) < cv_folds + 1:
            raise ValueError("Not enough unique dates for requested CV folds.")

        date_splitter = TimeSeriesSplit(n_splits=cv_folds)

        best_rmse: float | None = None
        best_model = None

        for fold_idx, (train_idx, val_idx) in enumerate(date_splitter.split(dates), start=1):
            train_dates = dates[train_idx]
            val_dates = dates[val_idx]

            df_train = df[df[date_col].isin(train_dates)]
            df_val = df[df[date_col].isin(val_dates)]

            X_train = df_train[feature_cols]
            y_train = df_train[target_col].to_numpy(dtype=np.float32)
            X_val = df_val[feature_cols]
            y_val = df_val[target_col].to_numpy(dtype=np.float32)

            candidate = LightGBMForecaster(self.cfg)
            candidate.fit(X_train, y_train, X_val, y_val, **lgbm_fit_kwargs)
            y_hat = candidate.predict(X_val)
            rmse = float(mean_squared_error(y_val, y_hat, squared=False))

            console.print(f"CV fold {fold_idx}/{cv_folds}: RMSE={rmse:.5f}")

            if best_rmse is None or rmse < best_rmse:
                best_rmse = rmse
                best_model = candidate.model

        if best_model is None:
            raise RuntimeError("CV failed to produce a best model.")

        self.model = best_model
        return self

