from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.dataset as ds
from rich.console import Console

from horizoncast.evaluation.business_cost import inventory_cost
from horizoncast.evaluation.metrics import coverage, interval_width, mae, pinball_loss, rmse
from horizoncast.features.classical import build_classical_features
from horizoncast.models.conformal import ConformalConfig, MAPIEConformalRegressor
from horizoncast.models.forecaster import LightGBMForecaster, LightGBMForecasterConfig

console = Console()


@dataclass(frozen=True)
class TrainEvalConfig:
    splits_dir: Path
    embeddings_dir: Path
    out_dir: Path
    pca_components: int = 8
    train_lookback_days: int = 365
    conformal_alpha: float = 0.1
    holding_cost: float = 0.1
    stockout_cost: float = 0.5
    max_series: int = 2000
    full_mode: bool = False
    export_shap: bool = True
    shap_sample_rows: int = 5000


def _read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def _read_train_tail(train_path: Path, lookback_days: int) -> pd.DataFrame:
    """
    Read only the most recent `lookback_days` from train parquet for memory safety.
    """
    dataset = ds.dataset(train_path, format="parquet")
    max_date = None
    for b in dataset.to_batches(columns=["date"], batch_size=250_000):
        m = pc.max(b.column("date")).as_py()
        if m is not None:
            m = pd.Timestamp(m)
            max_date = m if max_date is None else max(max_date, m)
    if max_date is None:
        raise RuntimeError(f"Could not read max date from {train_path}.")

    min_date = max_date - pd.Timedelta(days=lookback_days - 1)
    f = pc.greater_equal(
        ds.field("date"),
        min_date.to_pydatetime(),
    )
    table = dataset.to_table(filter=f)
    # Date nulls are not expected in this pipeline; avoid extra copies that can
    # trigger memory spikes on large windows.
    out = table.to_pandas()
    return out


def _merge_embeddings(df: pd.DataFrame, embeddings_dir: Path, pca_components: int) -> pd.DataFrame:
    prod_path = embeddings_dir / f"product_embeddings_pca{pca_components}.parquet"
    evt_path = embeddings_dir / f"event_embeddings_pca{pca_components}.parquet"
    if not prod_path.exists() or not evt_path.exists():
        raise FileNotFoundError(
            f"Expected embedding files in {embeddings_dir}: "
            f"{prod_path.name}, {evt_path.name}."
        )

    prod = pd.read_parquet(prod_path)
    evt = pd.read_parquet(evt_path)
    evt["date"] = pd.to_datetime(evt["date"], errors="coerce")

    out = df.merge(prod, on=["item_id", "store_id"], how="left")
    out = out.merge(evt, on=["date"], how="left")
    return out


def _prep_features(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    embeddings_dir: Path,
    pca_components: int,
):
    # Build features in chronological order on concatenated frames to ensure lags
    # for val/test can look back into prior periods without leakage from the future.
    console.print("[bold]Merging embedding features[/bold]")
    train_df = _merge_embeddings(train_df, embeddings_dir, pca_components)
    val_df = _merge_embeddings(val_df, embeddings_dir, pca_components)
    test_df = _merge_embeddings(test_df, embeddings_dir, pca_components)

    train_df["split"] = "train"
    val_df["split"] = "val"
    test_df["split"] = "test"
    all_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    all_df["date"] = pd.to_datetime(all_df["date"], errors="coerce")

    console.print("[bold]Building classical features[/bold]")
    feat_df, enc = build_classical_features(all_df, fit_encoders=True)
    num_cols = feat_df.select_dtypes(include=[np.number]).columns.tolist()
    feat_df[num_cols] = feat_df[num_cols].fillna(0.0)

    drop_cols = {"sales"}
    feature_cols = [c for c in num_cols if c not in drop_cols]

    tr = feat_df[feat_df["split"] == "train"].copy()
    va = feat_df[feat_df["split"] == "val"].copy()
    te = feat_df[feat_df["split"] == "test"].copy()
    _ = enc
    return tr, va, te, feature_cols


def run_train_eval(cfg: TrainEvalConfig) -> dict[str, float]:
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    train_path = cfg.splits_dir / "train.parquet"
    val_path = cfg.splits_dir / "val.parquet"
    test_path = cfg.splits_dir / "test.parquet"
    for p in (train_path, val_path, test_path):
        if not p.exists():
            raise FileNotFoundError(f"Missing {p}")

    console.print(f"[bold]Reading train tail[/bold] ({cfg.train_lookback_days} days)")
    train_df = _read_train_tail(train_path, cfg.train_lookback_days)
    console.print("[bold]Reading val/test[/bold]")
    val_df = _read_parquet(val_path)
    test_df = _read_parquet(test_path)

    series_cols = ["item_id", "store_id"]
    all_series = train_df[series_cols].drop_duplicates().reset_index(drop=True)
    if not cfg.full_mode:
        all_series = all_series.head(cfg.max_series)

    chunk_size = max(1, int(cfg.max_series))
    n_chunks = int(np.ceil(len(all_series) / chunk_size))
    console.print(f"[bold]Series plan[/bold]: {len(all_series):,} series across {n_chunks} chunk(s)")

    chunk_metrics: list[dict[str, float]] = []
    chunk_pred_paths: list[Path] = []
    shap_chunks: list[pd.DataFrame] = []

    for chunk_idx in range(n_chunks):
        s = chunk_idx * chunk_size
        e = min((chunk_idx + 1) * chunk_size, len(all_series))
        uniq = all_series.iloc[s:e]

        tr_df = train_df.merge(uniq, on=series_cols, how="inner")
        va_df = val_df.merge(uniq, on=series_cols, how="inner")
        te_df = test_df.merge(uniq, on=series_cols, how="inner")
        console.print(
            f"[bold]Chunk {chunk_idx + 1}/{n_chunks}[/bold]: "
            f"series={len(uniq):,} rows(train/val/test)=({len(tr_df):,}/{len(va_df):,}/{len(te_df):,})"
        )

        tr, va, te, feature_cols = _prep_features(
            train_df=tr_df,
            val_df=va_df,
            test_df=te_df,
            embeddings_dir=cfg.embeddings_dir,
            pca_components=cfg.pca_components,
        )
        console.print(f"[bold]Prepared features[/bold]: {len(feature_cols)} columns")

        X_train = tr[feature_cols]
        y_train = tr["sales"].to_numpy(dtype=np.float32)
        X_val = va[feature_cols]
        y_val = va["sales"].to_numpy(dtype=np.float32)
        X_test = te[feature_cols]
        y_test = te["sales"].to_numpy(dtype=np.float32)

        model = LightGBMForecaster(LightGBMForecasterConfig())
        console.print("[bold]Training LightGBM[/bold]")
        model.fit(X_train, y_train, X_val, y_val)

        y_val_pred = model.predict(X_val)
        y_test_pred = model.predict(X_test)

        conformal = MAPIEConformalRegressor(ConformalConfig(alpha=cfg.conformal_alpha))
        console.print("[bold]Fitting MAPIE conformal[/bold] on val split")
        conformal.fit(model.model, X_val, y_val)
        y_test_point, y_test_pi = conformal.predict(X_test, alpha=cfg.conformal_alpha)

        pi = np.asarray(y_test_pi)
        if pi.ndim == 3:
            y_lower = pi[:, 0, 0]
            y_upper = pi[:, 1, 0]
        elif pi.ndim == 2:
            y_lower = pi[:, 0]
            y_upper = pi[:, 1]
        else:
            raise RuntimeError(f"Unexpected MAPIE interval shape: {pi.shape}")

        q_lo = cfg.conformal_alpha / 2.0
        q_hi = 1.0 - q_lo

        metrics = {
            "chunk_idx": float(chunk_idx),
            "n_test_rows": float(len(y_test)),
            "val_rmse": rmse(y_val, y_val_pred),
            "val_mae": mae(y_val, y_val_pred),
            "test_rmse": rmse(y_test, y_test_pred),
            "test_mae": mae(y_test, y_test_pred),
            "test_coverage": coverage(y_test, y_lower, y_upper),
            "test_interval_width": interval_width(y_lower, y_upper),
            "test_pinball_loss": pinball_loss(y_test, y_lower, y_upper, q_lo, q_hi),
            "test_business_cost": inventory_cost(
                y_test,
                y_test_pred,
                holding_cost=cfg.holding_cost,
                stockout_cost=cfg.stockout_cost,
            ),
        }
        chunk_metrics.append(metrics)

        pred_out = te[["date", "item_id", "store_id"]].copy()
        pred_out["y_true"] = y_test
        pred_out["y_pred"] = np.asarray(y_test_point, dtype=np.float32)
        pred_out["y_lower"] = np.asarray(y_lower, dtype=np.float32)
        pred_out["y_upper"] = np.asarray(y_upper, dtype=np.float32)
        pred_path = cfg.out_dir / f"test_predictions_with_intervals_chunk_{chunk_idx:04d}.parquet"
        pred_out.to_parquet(pred_path, index=False)
        chunk_pred_paths.append(pred_path)

        if cfg.export_shap:
            booster = model.model
            if booster is None:
                raise RuntimeError("LightGBM model is unexpectedly None after fit.")
            sample_n = min(int(cfg.shap_sample_rows), len(X_test))
            shap_x = X_test.sample(n=sample_n, random_state=42) if sample_n < len(X_test) else X_test
            # LightGBM pred_contrib returns per-feature contributions and one expected value column.
            contrib = np.asarray(booster.predict(shap_x, pred_contrib=True), dtype=np.float64)
            feat_names = list(feature_cols)
            if contrib.ndim != 2 or contrib.shape[1] != len(feat_names) + 1:
                raise RuntimeError(f"Unexpected SHAP contribution shape from LightGBM: {contrib.shape}")
            feat_contrib = contrib[:, : len(feat_names)]
            mean_shap = np.mean(feat_contrib, axis=0)
            shap_chunks.append(
                pd.DataFrame(
                    {
                        "feature": feat_names,
                        "shap_value": mean_shap.astype(np.float32),
                        "n_rows": np.full(len(feat_names), sample_n, dtype=np.int32),
                        "chunk_idx": np.full(len(feat_names), chunk_idx, dtype=np.int32),
                    }
                )
            )

    metrics_df = pd.DataFrame(chunk_metrics)
    w = metrics_df["n_test_rows"].to_numpy(dtype=np.float64)
    w = w / w.sum()

    summary = {
        "val_rmse": float(np.sum(w * metrics_df["val_rmse"].to_numpy(dtype=np.float64))),
        "val_mae": float(np.sum(w * metrics_df["val_mae"].to_numpy(dtype=np.float64))),
        "test_rmse": float(np.sum(w * metrics_df["test_rmse"].to_numpy(dtype=np.float64))),
        "test_mae": float(np.sum(w * metrics_df["test_mae"].to_numpy(dtype=np.float64))),
        "test_coverage": float(np.sum(w * metrics_df["test_coverage"].to_numpy(dtype=np.float64))),
        "test_interval_width": float(np.sum(w * metrics_df["test_interval_width"].to_numpy(dtype=np.float64))),
        "test_pinball_loss": float(np.sum(w * metrics_df["test_pinball_loss"].to_numpy(dtype=np.float64))),
        "test_business_cost": float(np.sum(w * metrics_df["test_business_cost"].to_numpy(dtype=np.float64))),
    }

    all_preds = pd.concat([pd.read_parquet(p) for p in chunk_pred_paths], ignore_index=True)
    all_preds.to_parquet(cfg.out_dir / "test_predictions_with_intervals.parquet", index=False)
    metrics_df.to_json(cfg.out_dir / "metrics_chunks.json", orient="records", indent=2)
    pd.DataFrame([summary]).to_json(cfg.out_dir / "metrics.json", orient="records", indent=2)

    if cfg.export_shap and shap_chunks:
        shap_df = pd.concat(shap_chunks, ignore_index=True)
        weighted = shap_df.assign(weighted_shap=shap_df["shap_value"] * shap_df["n_rows"])
        grouped = (
            weighted.groupby("feature", as_index=False)[["weighted_shap", "n_rows"]]
            .sum()
            .assign(shap_value=lambda d: d["weighted_shap"] / d["n_rows"])
            [["feature", "shap_value"]]
        )
        grouped.to_parquet(cfg.out_dir / "shap_values.parquet", index=False)

    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train LightGBM + MAPIE and evaluate test intervals.")
    p.add_argument("--splits-dir", type=Path, default=Path("data/processed/splits"))
    p.add_argument("--embeddings-dir", type=Path, default=Path("data/processed/embeddings"))
    p.add_argument("--out-dir", type=Path, default=Path("data/processed/results"))
    p.add_argument("--pca-components", type=int, default=8)
    p.add_argument("--train-lookback-days", type=int, default=365)
    p.add_argument("--conformal-alpha", type=float, default=0.1)
    p.add_argument("--holding-cost", type=float, default=0.1)
    p.add_argument("--stockout-cost", type=float, default=0.5)
    p.add_argument("--max-series", type=int, default=2000, help="Limit number of item-store series for memory-safe runs.")
    p.add_argument("--full-mode", action="store_true", help="Process all series in chunks of --max-series.")
    p.add_argument("--no-export-shap", action="store_true", help="Disable SHAP export.")
    p.add_argument("--shap-sample-rows", type=int, default=5000, help="Rows sampled per chunk for SHAP export.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cfg = TrainEvalConfig(
        splits_dir=args.splits_dir,
        embeddings_dir=args.embeddings_dir,
        out_dir=args.out_dir,
        pca_components=args.pca_components,
        train_lookback_days=args.train_lookback_days,
        conformal_alpha=args.conformal_alpha,
        holding_cost=args.holding_cost,
        stockout_cost=args.stockout_cost,
        max_series=args.max_series,
        full_mode=args.full_mode,
        export_shap=not args.no_export_shap,
        shap_sample_rows=args.shap_sample_rows,
    )
    metrics = run_train_eval(cfg)
    console.print("[green]Done[/green]")
    for k, v in metrics.items():
        console.print(f"{k}: {v:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

