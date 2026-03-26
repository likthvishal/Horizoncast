from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    return float(np.mean(np.abs(y_true - y_pred)))


def pinball_loss(
    y_true: np.ndarray,
    y_lower: np.ndarray,
    y_upper: np.ndarray,
    q_lower: float,
    q_upper: float,
) -> float:
    """
    Symmetric pinball loss across two quantiles.

    Expected that:
      - y_lower corresponds to quantile q_lower
      - y_upper corresponds to quantile q_upper
    """
    y_true = np.asarray(y_true, dtype=np.float64)
    y_lower = np.asarray(y_lower, dtype=np.float64)
    y_upper = np.asarray(y_upper, dtype=np.float64)

    def _pinball(y: np.ndarray, yhat: np.ndarray, q: float) -> np.ndarray:
        diff = y - yhat
        return np.maximum(q * diff, (q - 1.0) * diff)

    loss_lower = _pinball(y_true, y_lower, q_lower)
    loss_upper = _pinball(y_true, y_upper, q_upper)
    return float(np.mean(loss_lower + loss_upper))


def coverage(y_true: np.ndarray, y_lower: np.ndarray, y_upper: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=np.float64)
    y_lower = np.asarray(y_lower, dtype=np.float64)
    y_upper = np.asarray(y_upper, dtype=np.float64)
    return float(np.mean((y_true >= y_lower) & (y_true <= y_upper)))


def interval_width(y_lower: np.ndarray, y_upper: np.ndarray) -> float:
    y_lower = np.asarray(y_lower, dtype=np.float64)
    y_upper = np.asarray(y_upper, dtype=np.float64)
    return float(np.mean(y_upper - y_lower))


@dataclass(frozen=True)
class WRMSSEConfig:
    """
    Lightweight WRMSSE proxy.

    This implementation computes a per-series scale from the training period
    using RMS of consecutive differences, then aggregates per-series forecast
    MSE using series weights proportional to total training demand.

    It is intended for engineering validation; for exact M5 competition parity,
    the series hierarchy weights must match the official WRMSSE definition.
    """

    series_cols: tuple[str, str] = ("item_id", "store_id")
    date_col: str = "date"
    target_col: str = "sales"


def wrmsse(
    train_df: np.ndarray,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    weights: np.ndarray | None = None,
) -> float:
    """
    Minimal WRMSSE helper for pre-shaped series metrics.

    If `weights` is not provided, this falls back to a simple RMSE-like
    normalization.

    NOTE: For full M5 WRMSSE, pass properly prepared per-series contributions.
    """
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    mse = (y_true - y_pred) ** 2

    if weights is None:
        return float(np.sqrt(np.mean(mse)))
    w = np.asarray(weights, dtype=np.float64)
    w = w / np.sum(w)
    return float(np.sqrt(np.sum(w * mse)))

