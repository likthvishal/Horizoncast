from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import os
import numpy as np
import pandas as pd
from rich.console import Console
from sklearn.decomposition import PCA

console = Console()

# Force a PyTorch-only Transformers/Sentence-Transformers import path.
# This avoids TensorFlow/Keras integration issues (e.g., Keras 3 compatibility)
# on environments where TF is not installed or not supported.
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")

from sentence_transformers import SentenceTransformer  # noqa: E402

@dataclass(frozen=True)
class LLMEnrichmentConfig:
    model_name: str = "all-MiniLM-L6-v2"
    batch_size: int = 64
    pca_components: int = 8


def _read_product_metadata_from_raw(raw_dir: Path) -> pd.DataFrame:
    """
    Read minimal item/store metadata from M5 raw `sales_train_validation.csv`.
    This is much faster than scanning the full `train.parquet`.
    """
    sales_path = raw_dir / "sales_train_validation.csv"
    if not sales_path.exists():
        raise FileNotFoundError(f"Missing {sales_path}. Put M5 CSVs under --raw-dir.")

    cols = ["item_id", "dept_id", "cat_id", "store_id", "state_id"]
    usecols = ["id"] + cols
    sales = pd.read_csv(sales_path, usecols=usecols)
    return sales[cols].drop_duplicates(subset=["item_id", "store_id"]).reset_index(drop=True)


def _read_event_rows_from_raw(raw_dir: Path) -> pd.DataFrame:
    """
    Read minimal calendar event metadata from raw `calendar.csv`.
    """
    cal_path = raw_dir / "calendar.csv"
    if not cal_path.exists():
        raise FileNotFoundError(f"Missing {cal_path}. Put M5 CSVs under --raw-dir.")

    usecols = ["date", "event_name_1", "event_type_1", "event_name_2", "event_type_2"]
    cal = pd.read_csv(cal_path, usecols=usecols)
    cal["date"] = pd.to_datetime(cal["date"], errors="coerce")
    return (
        cal.dropna(subset=["date"])
        .drop_duplicates(subset=["date"])
        .sort_values("date")
        .reset_index(drop=True)
    )


def build_product_text(items: pd.DataFrame) -> pd.Series:
    """
    Construct natural language descriptions per item-store pair.
    """
    return (
        items["item_id"].astype(str)
        + " is a "
        + items["cat_id"].astype(str)
        + " item in department "
        + items["dept_id"].astype(str)
        + ", sold in store "
        + items["store_id"].astype(str)
        + " in state "
        + items["state_id"].astype(str)
        + "."
    )


def build_event_text(events: pd.DataFrame) -> pd.Series:
    """
    Construct event context text per date row from M5 calendar fields.
    """
    def _one(row: pd.Series) -> str:
        parts: list[str] = []
        for i in (1, 2):
            en = row.get(f"event_name_{i}")
            et = row.get(f"event_type_{i}")
            if pd.notna(en) and str(en).strip():
                if pd.notna(et) and str(et).strip():
                    parts.append(f"{en} ({et})")
                else:
                    parts.append(str(en))
        if not parts:
            return "No special event."
        return "Calendar event(s): " + "; ".join(parts) + "."

    return events.apply(_one, axis=1)


def embed_texts(texts: list[str], cfg: LLMEnrichmentConfig) -> np.ndarray:
    model = SentenceTransformer(cfg.model_name)
    emb = model.encode(texts, batch_size=cfg.batch_size, show_progress_bar=True)
    return np.asarray(emb, dtype=np.float32)


def pca_reduce(embeddings: np.ndarray, n_components: int) -> tuple[np.ndarray, PCA]:
    pca = PCA(n_components=n_components, random_state=42)
    reduced = pca.fit_transform(embeddings).astype(np.float32)
    return reduced, pca


def compute_and_cache_embeddings(
    splits_dir: Path,
    out_dir: Path,
    raw_dir: Path,
    cfg: LLMEnrichmentConfig | None = None,
    force: bool = False,
) -> tuple[Path, Path]:
    """
    Compute two cached embedding feature tables:
    - product embeddings keyed by (item_id, store_id)
    - event embeddings keyed by date

    The heavy embeddings are computed once and saved as parquet.
    """
    cfg = cfg or LLMEnrichmentConfig()
    out_dir.mkdir(parents=True, exist_ok=True)

    # We keep `splits_dir` for pipeline consistency, but use `raw_dir` for
    # fast extraction of item/store and calendar metadata.
    _ = splits_dir

    product_out = out_dir / f"product_embeddings_pca{cfg.pca_components}.parquet"
    event_out = out_dir / f"event_embeddings_pca{cfg.pca_components}.parquet"

    if product_out.exists() and event_out.exists() and not force:
        console.print(f"[green]Using cached embeddings[/green] at {out_dir}")
        return product_out, event_out

    # PRODUCT EMBEDDINGS (unique item-store metadata)
    console.print("[bold]Extracting unique product metadata[/bold] (from raw CSV)")
    items = _read_product_metadata_from_raw(raw_dir)
    prod_text = build_product_text(items).tolist()

    console.print(f"[bold]Embedding products[/bold] ({len(prod_text):,} texts) with {cfg.model_name}")
    prod_emb = embed_texts(prod_text, cfg)
    prod_red, _ = pca_reduce(prod_emb, cfg.pca_components)

    prod_df = items[["item_id", "store_id"]].copy()
    for j in range(cfg.pca_components):
        prod_df[f"prod_emb_{j}"] = prod_red[:, j]
    prod_df.to_parquet(product_out, index=False)
    console.print(f"[green]Wrote[/green] {product_out}")

    # EVENT EMBEDDINGS (unique date/event rows)
    console.print("[bold]Extracting unique calendar event rows[/bold] (from raw CSV)")
    events = _read_event_rows_from_raw(raw_dir)

    evt_text = build_event_text(events).tolist()
    console.print(f"[bold]Embedding events[/bold] ({len(evt_text):,} texts) with {cfg.model_name}")
    evt_emb = embed_texts(evt_text, cfg)
    evt_red, _ = pca_reduce(evt_emb, cfg.pca_components)

    evt_df = events[["date"]].copy()
    for j in range(cfg.pca_components):
        evt_df[f"evt_emb_{j}"] = evt_red[:, j]
    evt_df.to_parquet(event_out, index=False)
    console.print(f"[green]Wrote[/green] {event_out}")

    return product_out, event_out


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute and cache LLM embedding enrichment features.")
    p.add_argument("--splits-dir", type=Path, default=Path("data/processed/splits"))
    p.add_argument("--raw-dir", type=Path, default=Path("data/raw"), help="Directory with raw M5 CSVs.")
    p.add_argument("--out-dir", type=Path, default=Path("data/processed/embeddings"))
    p.add_argument("--model-name", type=str, default=LLMEnrichmentConfig.model_name)
    p.add_argument("--batch-size", type=int, default=LLMEnrichmentConfig.batch_size)
    p.add_argument("--pca-components", type=int, default=LLMEnrichmentConfig.pca_components)
    p.add_argument("--force", action="store_true", help="Recompute even if cached files exist.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cfg = LLMEnrichmentConfig(
        model_name=args.model_name,
        batch_size=args.batch_size,
        pca_components=args.pca_components,
    )
    compute_and_cache_embeddings(args.splits_dir, args.out_dir, raw_dir=args.raw_dir, cfg=cfg, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

