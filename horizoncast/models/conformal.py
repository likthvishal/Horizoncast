from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass(frozen=True)
class ConformalConfig:
    """
    Conformal prediction config for calibrated interval estimates.
    """

    alpha: float = 0.1
    method: Literal["plus"] = "plus"
    cv: Literal["prefit"] = "prefit"


class MAPIEConformalRegressor:
    """
    Wrap a prefit regressor with MAPIE conformal interval prediction.
    """

    def __init__(self, cfg: ConformalConfig | None = None) -> None:
        self.cfg = cfg or ConformalConfig()
        self.mapie = None
        self._backend: str | None = None
        self.y_pred_: np.ndarray | None = None
        self.intervals_: np.ndarray | None = None

    def fit(
        self,
        estimator,
        X_calib,
        y_calib,
    ) -> "MAPIEConformalRegressor":
        try:
            # MAPIE >=1.0 API
            from mapie.regression import SplitConformalRegressor

            self.mapie = SplitConformalRegressor(
                estimator=estimator,
                confidence_level=1.0 - float(self.cfg.alpha),
                prefit=True,
            )
            self.mapie.conformalize(X_calib, y_calib)
            self._backend = "split_conformal"
        except Exception:
            try:
                # Older MAPIE API
                from mapie.regression import MapieRegressor

                self.mapie = MapieRegressor(
                    estimator=estimator,
                    method=self.cfg.method,
                    cv=self.cfg.cv,
                )
                self.mapie.fit(X_calib, y_calib)
                self._backend = "mapie_regressor"
            except Exception as e:  # pragma: no cover
                raise ImportError("MAPIE is not installed or incompatible. Please `pip install -U mapie`.") from e
        return self

    def predict(self, X_test, alpha: float | None = None):
        if self.mapie is None:
            raise RuntimeError("Call fit() before predict().")

        a = float(alpha if alpha is not None else self.cfg.alpha)
        if self._backend == "split_conformal":
            # SplitConformalRegressor uses confidence_level in constructor
            # and returns point + [lower, upper] via predict_interval.
            y_pred = self.mapie.predict(X_test)
            y_pred_i, bounds = self.mapie.predict_interval(X_test)
            _ = y_pred_i
            y_pis = np.asarray(bounds)
        else:
            y_pred, y_pis = self.mapie.predict(X_test, alpha=a)

        self.y_pred_ = np.asarray(y_pred)
        self.intervals_ = np.asarray(y_pis)
        return self.y_pred_, self.intervals_

