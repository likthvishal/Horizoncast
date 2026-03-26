# HorizonCast

**HorizonCast** is an end-to-end demand forecasting system built on the M5 Walmart dataset that combines:
- high-signal classical time-series features,
- LLM-enriched semantic embeddings,
- LightGBM forecasting,
- conformal prediction for calibrated uncertainty,
- and business-aware inventory cost evaluation.

It is designed like a production ML system: modular pipelines, cached artifacts, memory-safe execution on limited hardware, and an interactive dashboard for decision support.

---

## Why this project stands out

- **Hybrid modeling**: fuses classical demand signals (lags/rolling/calendar/price) with LLM-derived semantic features (product + event embeddings).
- **Uncertainty done right**: conformal prediction intervals via MAPIE with empirical coverage tracking, not just point forecasts.
- **Business-first evaluation**: adds asymmetric inventory cost (stockout vs holding) alongside RMSE/MAE.
- **Built for real constraints**: engineered to survive multi-million-row data workflows without crashing local machines.
- **Recruiter-ready execution**: clean package structure, CLI workflows, reproducible outputs, and an analytics dashboard.

---

## Architecture

1. **Data ingestion + preprocessing**
   - Ingests raw M5 CSVs
   - Melts/merges to tidy format
   - Produces train/val/test parquet splits

2. **Feature engineering**
   - Classical: lag, rolling stats, calendar/event, SNAP, and price dynamics
   - Categorical encodings for key retail entities
   - Optional LLM enrichment with `sentence-transformers` + PCA caching

3. **Modeling**
   - Baselines: Naive, Seasonal Naive, Prophet (subset-capable)
   - Main model: `LightGBMRegressor` with early stopping
   - Uncertainty: MAPIE conformal layer

4. **Evaluation**
   - RMSE, MAE, Pinball loss
   - Coverage + interval width
   - Inventory business cost (asymmetric penalties)
   - Ablation harness support

5. **Visualization**
   - Streamlit + Plotly dashboard
   - KPI cards, interval plots, error histograms, prediction tables
   - SHAP feature importance panel from exported `shap_values.parquet`

---

## What we solved: memory and robustness engineering

This project originally hit multiple real-world failure points (OOM, dependency/API drift). The pipeline now includes targeted engineering fixes:

- **Memory-safe train loading** with pyarrow dataset filtering (`_read_train_tail`) to avoid loading full history.
- **Removed copy-heavy operations** (`dropna` patterns causing expensive dataframe duplication).
- **Type-safe null handling** (`fillna` only on numeric columns to avoid StringArray failures).
- **Series throttling for constrained machines** via `--max-series`.
- **Full dataset mode without OOM** via chunked execution (`--full-mode`) that:
  - processes all item-store series in chunks,
  - writes per-chunk predictions,
  - aggregates weighted metrics into final artifacts.
- **Dependency compatibility hardening**:
  - lazy imports + graceful errors for LightGBM/MAPIE,
  - MAPIE API bridging (`SplitConformalRegressor` vs `MapieRegressor`),
  - transformer backend controls for Keras compatibility.

---

## Latest validated run (example)

From a successful run of `train_and_evaluate`:
- `val_rmse`: **1.6646**
- `val_mae`: **0.8783**
- `test_rmse`: **1.7162**
- `test_mae`: **0.8933**
- `test_coverage`: **0.8983**
- `test_interval_width`: **3.6510**
- `test_pinball_loss`: **0.3812**
- `test_business_cost`: **0.2547**

These results show a balanced profile: strong point accuracy with interval coverage close to target.

---

## Quick start

### 1) Install
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Download M5 data
Get the files from Kaggle: [M5 Forecasting Accuracy](https://www.kaggle.com/c/m5-forecasting-accuracy/data)

Place under `data/raw/`:
- `sales_train_validation.csv`
- `calendar.csv`
- `sell_prices.csv`

### 3) Build processed data
```bash
python -m horizoncast.data.download --raw-dir data/raw --out data/processed/m5_merged.parquet
python -m horizoncast.data.preprocess --in data/processed/m5_merged.parquet --out-dir data/processed/splits
```

### 4) Build LLM enrichment features
```bash
python -m horizoncast.features.llm_enrichment --raw-dir data/raw --out-dir data/processed/embeddings --pca-components 8
```

### 5) Train + evaluate (memory-safe subset)
```bash
python -m horizoncast.models.train_and_evaluate --max-series 2000
```

### 6) Train + evaluate full dataset in chunks
```bash
python -m horizoncast.models.train_and_evaluate --full-mode --max-series 2000 --shap-sample-rows 5000
```

Outputs are written to `data/processed/results/`:
- `metrics.json`
- `metrics_chunks.json`
- `test_predictions_with_intervals.parquet`
- `shap_values.parquet` (unless disabled)

### 7) Launch dashboard
```bash
streamlit run horizoncast/dashboard/app.py
```

---

## Repository layout

Core package: `horizoncast/`
- `data/`: ingestion and preprocessing
- `features/`: classical + LLM enrichment
- `models/`: baselines, LightGBM wrapper, conformal layer, train/eval runner
- `evaluation/`: metrics, business cost, ablation utilities
- `dashboard/`: Streamlit app

---

## Interview-ready discussion points

- How to combine semantic context (LLM embeddings) with tabular time-series features.
- How conformal prediction gives practical uncertainty guarantees in forecasting.
- How to design ML systems for limited-memory environments without sacrificing extensibility.
- How to evaluate models not just statistically, but with explicit business cost functions.
