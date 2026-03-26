from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def _load_metrics(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    df = pd.read_json(path)
    if df.empty:
        return {}
    row = df.iloc[0].to_dict()
    return {str(k): float(v) for k, v in row.items()}


def _load_predictions(path: Path, sample_rows: int = 200_000) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    if len(df) > sample_rows:
        df = df.sample(sample_rows, random_state=42)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"]).sort_values("date")


def main() -> None:
    st.set_page_config(page_title="HorizonCast Dashboard", layout="wide")
    st.title("HorizonCast Forecast Dashboard")

    default_results = Path("data/processed/results")
    results_dir = Path(st.sidebar.text_input("Results directory", str(default_results)))
    metrics_path = results_dir / "metrics.json"
    preds_path = results_dir / "test_predictions_with_intervals.parquet"

    metrics = _load_metrics(metrics_path)
    preds = _load_predictions(preds_path)

    if not metrics:
        st.warning(f"No metrics found at `{metrics_path}`.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Test RMSE", f"{metrics.get('test_rmse', float('nan')):.4f}")
        c2.metric("Test MAE", f"{metrics.get('test_mae', float('nan')):.4f}")
        c3.metric("Coverage", f"{metrics.get('test_coverage', float('nan')):.4f}")
        c4.metric("Business Cost", f"{metrics.get('test_business_cost', float('nan')):.4f}")

        with st.expander("All metrics"):
            st.json(metrics)

    if preds.empty:
        st.warning(f"No predictions found at `{preds_path}`.")
        return

    st.subheader("Prediction Intervals Over Time")
    series_df = (
        preds.groupby("date", as_index=False)[["y_true", "y_pred", "y_lower", "y_upper"]]
        .mean()
        .sort_values("date")
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series_df["date"],
            y=series_df["y_upper"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=series_df["date"],
            y=series_df["y_lower"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            name="Prediction Interval",
            hoverinfo="skip",
        )
    )
    fig.add_trace(go.Scatter(x=series_df["date"], y=series_df["y_true"], mode="lines", name="Actual"))
    fig.add_trace(go.Scatter(x=series_df["date"], y=series_df["y_pred"], mode="lines", name="Predicted"))
    fig.update_layout(height=420, margin=dict(l=8, r=8, t=8, b=8))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Error Distribution")
    preds["error"] = preds["y_pred"] - preds["y_true"]
    hist = px.histogram(preds, x="error", nbins=80, title="Prediction Error Histogram")
    hist.update_layout(height=350, margin=dict(l=8, r=8, t=28, b=8))
    st.plotly_chart(hist, use_container_width=True)

    st.subheader("Sample Predictions")
    st.dataframe(preds.head(200), use_container_width=True)

    st.subheader("SHAP (Optional)")
    shap_path = results_dir / "shap_values.parquet"
    if shap_path.exists():
        shap_df = pd.read_parquet(shap_path)
        expected = {"feature", "shap_value"}
        if expected.issubset(shap_df.columns):
            top = (
                shap_df.assign(abs_shap=shap_df["shap_value"].abs())
                .groupby("feature", as_index=False)["abs_shap"]
                .mean()
                .sort_values("abs_shap", ascending=False)
                .head(20)
            )
            shap_fig = px.bar(top, x="abs_shap", y="feature", orientation="h", title="Top Features by Mean |SHAP|")
            shap_fig.update_layout(height=500, margin=dict(l=8, r=8, t=28, b=8), yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(shap_fig, use_container_width=True)
        else:
            st.info("`shap_values.parquet` found, but expected columns are missing: `feature`, `shap_value`.")
    else:
        st.info("No `shap_values.parquet` found yet. Add SHAP export in the training pipeline to enable this panel.")


if __name__ == "__main__":
    main()

