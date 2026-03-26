from __future__ import annotations

import numpy as np


def inventory_cost(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    holding_cost: float = 0.1,
    stockout_cost: float = 0.5,
) -> float:
    """
    Asymmetric business cost for forecast errors.

    - Over-forecasting (y_pred > y_true): holding_cost per unit
    - Under-forecasting (y_pred < y_true): stockout_cost per unit
    """
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    err = y_pred - y_true
    over_mask = err > 0
    under_mask = ~over_mask
    cost = np.where(over_mask, holding_cost * err, stockout_cost * (-err))
    return float(np.mean(cost))

