from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd
from rich.console import Console

console = Console()

SERIES_COLS: Final[tuple[str, str]] = ("item_id", "store_id")
DATE_COL: Final[str] = "date"


@dataclass(frozen=True)
class NaiveBaselineConfig:
    """
    One-step naive baseline with recursive forecasting over a horizon.

    For each predicted day, the baseline uses the previous day's forecast
    (initially seeded from the last row in `history_df`).
    """

    series_cols: tuple[str, str] = SERIES_COLS
    date_col: str = DATE_COL


class NaiveForecaster:
    def __init__(self, cfg: NaiveBaselineConfig | None = None) -> None:
        self.cfg = cfg or NaiveBaselineConfig()
        self._last_date: pd.Timestamp | None = None
        self._last_sales: dict[tuple[str, str], float] = {}

    def fit(self, history_df: pd.DataFrame) -> "NaiveForecaster":
        req = {self.cfg.series_cols[0], self.cfg.series_cols[1], self.cfg.date_col, "sales"}
        missing = req.difference(history_df.columns)
        if missing:
            raise ValueError(f"history_df missing required columns: {sorted(missing)}")

        df = history_df.copy()
        df[self.cfg.date_col] = pd.to_datetime(df[self.cfg.date_col], errors="coerce")
        df = df.dropna(subset=[self.cfg.date_col])

        last_date = df[self.cfg.date_col].max()
        if pd.isna(last_date):
            raise ValueError("Could not infer last date from history_df.")

        seed = df[df[self.cfg.date_col] == last_date]
        series0 = self.cfg.series_cols[0]
        series1 = self.cfg.series_cols[1]
        self._last_sales = {
            (str(r[series0]), str(r[series1])): float(r["sales"]) for r in seed[[series0, series1, "sales"]].itertuples(index=False)
        }
        self._last_date = pd.Timestamp(last_date)
        return self

    def predict(self, future_df: pd.DataFrame) -> np.ndarray:
        if self._last_date is None:
            raise RuntimeError("Call fit() before predict().")

        req = {self.cfg.series_cols[0], self.cfg.series_cols[1], self.cfg.date_col}
        missing = req.difference(future_df.columns)
        if missing:
            raise ValueError(f"future_df missing required columns: {sorted(missing)}")

        df = future_df.copy()
        df[self.cfg.date_col] = pd.to_datetime(df[self.cfg.date_col], errors="coerce")
        df = df.dropna(subset=[self.cfg.date_col]).reset_index(drop=True)

        series0 = self.cfg.series_cols[0]
        series1 = self.cfg.series_cols[1]

        # Predict in date order, updating the per-series "last sales" recursively.
        out = np.empty(len(df), dtype=np.float32)
        # Keep original indices (from df) so assignments match `out`.
        df_sorted = df.sort_values(self.cfg.date_col)

        last_sales = dict(self._last_sales)
        current_last_date = self._last_date

        for _, g in df_sorted.groupby(self.cfg.date_col, sort=True):
            preds = []
            for r in g[[series0, series1]].itertuples(index=False, name=None):
                key = (str(r[0]), str(r[1]))
                preds.append(last_sales.get(key, 0.0))
            preds_arr = np.asarray(preds, dtype=np.float32)
            # Update last_sales for the next day horizon step.
            for r, p in zip(g[[series0, series1]].itertuples(index=False, name=None), preds_arr):
                key = (str(r[0]), str(r[1]))
                last_sales[key] = float(p)

            out[g.index.values] = preds_arr
        # `future_df` and `df` align because we reset_index(drop=True) after dropping null dates.
        return out


@dataclass(frozen=True)
class SeasonalNaiveConfig:
    seasonal_lag_days: int = 364  # approx 1 year (M5 uses same weekday patterns)


class SeasonalNaiveForecaster:
    """
    Seasonal naive baseline using `sales` from t - seasonal_lag_days.

    Implementation uses history_df passed to `fit()` and expects history_df to
    contain sales for the lookup dates.
    """

    def __init__(self, cfg: SeasonalNaiveConfig | None = None) -> None:
        self.cfg = cfg or SeasonalNaiveConfig()
        self._history: pd.DataFrame | None = None

    def fit(self, history_df: pd.DataFrame) -> "SeasonalNaiveForecaster":
        req = {SERIES_COLS[0], SERIES_COLS[1], DATE_COL, "sales"}
        missing = req.difference(history_df.columns)
        if missing:
            raise ValueError(f"history_df missing required columns: {sorted(missing)}")
        self._history = history_df.copy()
        self._history[DATE_COL] = pd.to_datetime(self._history[DATE_COL], errors="coerce")
        self._history = self._history.dropna(subset=[DATE_COL])
        return self

    def predict(self, future_df: pd.DataFrame) -> np.ndarray:
        if self._history is None:
            raise RuntimeError("Call fit() before predict().")

        h = self._history[[SERIES_COLS[0], SERIES_COLS[1], DATE_COL, "sales"]].copy()
        f = future_df.copy()
        f[DATE_COL] = pd.to_datetime(f[DATE_COL], errors="coerce")
        f = f.dropna(subset=[DATE_COL])

        f["lookup_date"] = f[DATE_COL] - pd.Timedelta(days=self.cfg.seasonal_lag_days)
        merged = f.merge(
            h,
            left_on=[SERIES_COLS[0], SERIES_COLS[1], "lookup_date"],
            right_on=[SERIES_COLS[0], SERIES_COLS[1], DATE_COL],
            how="left",
            suffixes=("", "_hist"),
        )
        # If lookup is missing, fall back to 0.
        preds = merged["sales"].fillna(0.0).astype("float32").to_numpy()
        return preds


class ProphetForecaster:
    """
    Prophet baseline.

    Prophet is expensive to fit per-item series at M5 scale, so this
    implementation is intended for small subsets or ablation demos.
    """

    def __init__(self, max_series: int = 50) -> None:
        self.max_series = max_series
        self._models: dict[tuple[str, str], object] = {}

    def fit(self, history_df: pd.DataFrame) -> "ProphetForecaster":
        try:
            from prophet import Prophet
        except Exception as e:  # pragma: no cover
            raise ImportError("Prophet is not installed. Install prophet>=1.1.") from e

        req = {SERIES_COLS[0], SERIES_COLS[1], DATE_COL, "sales"}
        missing = req.difference(history_df.columns)
        if missing:
            raise ValueError(f"history_df missing required columns: {sorted(missing)}")

        df = history_df.copy()
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
        df = df.dropna(subset=[DATE_COL])

        series_ids = df[[SERIES_COLS[0], SERIES_COLS[1]]].drop_duplicates()
        if len(series_ids) > self.max_series:
            console.print(f"[yellow]Prophet baseline limited to first {self.max_series} series for feasibility.[/yellow]")
            series_ids = series_ids.head(self.max_series)

        self._models = {}
        for (item_id, store_id), g in df.groupby(SERIES_COLS, sort=False):
            if len(self._models) >= self.max_series:
                break
            model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
            prophet_df = g.rename(columns={DATE_COL: "ds", "sales": "y"})[["ds", "y"]].sort_values("ds")
            model.fit(prophet_df)
            self._models[(str(item_id), str(store_id))] = model
        return self

    def predict(self, future_df: pd.DataFrame) -> np.ndarray:
        f = future_df.copy()
        f[DATE_COL] = pd.to_datetime(f[DATE_COL], errors="coerce")
        f = f.dropna(subset=[DATE_COL])

        preds = np.zeros(len(f), dtype=np.float32)
        for idx, r in f.reset_index(drop=True).iterrows():
            key = (str(r[SERIES_COLS[0]]), str(r[SERIES_COLS[1]]))
            model = self._models.get(key)
            if model is None:
                preds[idx] = 0.0
                continue
            future = pd.DataFrame({"ds": [r[DATE_COL]]})
            yhat = model.predict(future)["yhat"].iloc[0]
            preds[idx] = float(yhat)
        return preds

