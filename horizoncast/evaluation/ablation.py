from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class AblationResult:
    name: str
    metric: float


def run_ablation(
    candidates: dict[str, Callable[[object], object]],
    fit_fn,
    predict_fn,
    score_fn: Callable[[np.ndarray, np.ndarray], float],
    X: object,
    y_true: np.ndarray,
) -> list[AblationResult]:
    """
    Generic ablation harness.

    - `candidates` maps a name to a function that transforms `X`/features.
    - `fit_fn` fits a model given transformed features.
    - `predict_fn` predicts using the fitted model.
    - `score_fn` scores (y_true, y_pred).
    """
    results: list[AblationResult] = []
    for name, transform in candidates.items():
        Xc = transform(X)
        model = fit_fn(Xc)
        y_pred = predict_fn(model, Xc)
        m = float(score_fn(y_true, np.asarray(y_pred)))
        results.append(AblationResult(name=name, metric=m))

    results.sort(key=lambda r: r.metric)
    return results

