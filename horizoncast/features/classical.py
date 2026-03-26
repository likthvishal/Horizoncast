from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


@dataclass(frozen=True)
class ClassicalFeatureConfig:
    lags: tuple[int, ...] = (7, 14, 28)
    rolling_windows: tuple[int, ...] = (7, 14, 28)


def _ensure_sorted(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(["store_id", "item_id", "date"]).reset_index(drop=True)


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["day_of_week"] = out["date"].dt.dayofweek.astype("int16")
    out["month"] = out["date"].dt.month.astype("int16")
    out["year"] = out["date"].dt.year.astype("int16")
    out["is_weekend"] = (out["day_of_week"] >= 5).astype("int8")

    # M5 calendar event flags
    event_cols = [c for c in out.columns if c.startswith("event_name_") or c.startswith("event_type_")]
    if event_cols:
        out["is_event"] = out[event_cols].notna().any(axis=1).astype("int8")
    else:
        out["is_event"] = 0

    snap_cols = [c for c in out.columns if c.startswith("snap_")]
    if snap_cols:
        out["snap_flag"] = out[snap_cols].fillna(0).max(axis=1).astype("int8")
    else:
        out["snap_flag"] = 0

    return out


def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "sell_price" not in out.columns:
        out["sell_price"] = np.nan

    out = _ensure_sorted(out)

    out["price_change_pct"] = (
        out.groupby(["store_id", "item_id"], sort=False)["sell_price"].pct_change().replace([np.inf, -np.inf], np.nan)
    ).astype("float32")

    store_mean = out.groupby(["store_id", "item_id"], sort=False)["sell_price"].transform("mean")
    out["price_vs_store_mean"] = (out["sell_price"] / store_mean).astype("float32")
    return out


def add_lag_rolling_features(df: pd.DataFrame, cfg: ClassicalFeatureConfig | None = None) -> pd.DataFrame:
    cfg = cfg or ClassicalFeatureConfig()
    out = _ensure_sorted(df.copy())

    g = out.groupby(["store_id", "item_id"], sort=False)["sales"]

    for lag in cfg.lags:
        out[f"lag_{lag}"] = g.shift(lag).astype("float32")

    for w in cfg.rolling_windows:
        # roll on lag_1 to avoid leakage from current day
        s = g.shift(1)
        out[f"roll_mean_{w}"] = s.rolling(w).mean().astype("float32")
        out[f"roll_std_{w}"] = s.rolling(w).std(ddof=0).astype("float32")
        out[f"roll_max_{w}"] = s.rolling(w).max().astype("float32")

    return out


@dataclass
class CategoricalEncoders:
    item_id: LabelEncoder
    dept_id: LabelEncoder
    store_id: LabelEncoder
    state_id: LabelEncoder
    cat_id: LabelEncoder


def fit_categorical_encoders(df: pd.DataFrame) -> CategoricalEncoders:
    def fit(col: str) -> LabelEncoder:
        le = LabelEncoder()
        le.fit(df[col].astype(str))
        return le

    return CategoricalEncoders(
        item_id=fit("item_id"),
        dept_id=fit("dept_id"),
        store_id=fit("store_id"),
        state_id=fit("state_id"),
        cat_id=fit("cat_id"),
    )


def transform_categoricals(df: pd.DataFrame, enc: CategoricalEncoders) -> pd.DataFrame:
    out = df.copy()
    out["item_id_le"] = enc.item_id.transform(out["item_id"].astype(str)).astype("int32")
    out["dept_id_le"] = enc.dept_id.transform(out["dept_id"].astype(str)).astype("int16")
    out["store_id_le"] = enc.store_id.transform(out["store_id"].astype(str)).astype("int16")
    out["state_id_le"] = enc.state_id.transform(out["state_id"].astype(str)).astype("int16")
    out["cat_id_le"] = enc.cat_id.transform(out["cat_id"].astype(str)).astype("int16")
    return out


def build_classical_features(
    df: pd.DataFrame,
    cfg: ClassicalFeatureConfig | None = None,
    encoders: CategoricalEncoders | None = None,
    fit_encoders: bool = True,
) -> tuple[pd.DataFrame, CategoricalEncoders]:
    """
    Build classical time-series and calendar/price features.

    Returns (df_with_features, encoders).
    """
    out = df.copy()
    if "date" not in out.columns:
        raise ValueError("Expected a 'date' column.")
    out["date"] = pd.to_datetime(out["date"], errors="coerce")

    out = add_calendar_features(out)
    out = add_price_features(out)
    out = add_lag_rolling_features(out, cfg=cfg)

    if encoders is None and fit_encoders:
        encoders = fit_categorical_encoders(out)
    if encoders is None:
        raise ValueError("Encoders not provided and fit_encoders=False.")

    out = transform_categoricals(out, encoders)
    return out, encoders

