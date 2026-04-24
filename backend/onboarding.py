"""Customer onboarding flows and templates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class OnboardingStep:
    """An onboarding step."""

    id: str
    title: str
    description: str
    action_url: Optional[str] = None
    estimated_duration_minutes: int = 5


ONBOARDING_FLOW = [
    OnboardingStep(
        id="account",
        title="Create Account",
        description="Set up your HorizonCast account",
        estimated_duration_minutes=5,
    ),
    OnboardingStep(
        id="upload",
        title="Upload First Dataset",
        description="Upload your sales or demand data (CSV or Parquet)",
        action_url="/datasets/upload",
        estimated_duration_minutes=10,
    ),
    OnboardingStep(
        id="train",
        title="Train Your Model",
        description="Start training your first forecast model",
        action_url="/models/train",
        estimated_duration_minutes=15,
    ),
    OnboardingStep(
        id="predict",
        title="Make Predictions",
        description="Use your trained model to forecast future demand",
        action_url="/forecasts/predict",
        estimated_duration_minutes=5,
    ),
    OnboardingStep(
        id="explore",
        title="Explore Results",
        description="View metrics, explanations, and uncertainty intervals",
        action_url="/dashboard",
        estimated_duration_minutes=10,
    ),
]


QUICKSTART_TEMPLATES = {
    "retail": {
        "name": "Retail Store Forecast",
        "description": "Forecast daily sales for retail stores",
        "sample_data_url": "https://...m5-sample-data.csv",
        "recommended_config": {
            "train_lookback_days": 365,
            "holding_cost": 0.1,
            "stockout_cost": 0.5,
        },
    },
    "ecommerce": {
        "name": "E-Commerce Demand",
        "description": "Forecast product demand for e-commerce",
        "sample_data_url": "https://.../ecommerce-sample.csv",
        "recommended_config": {
            "train_lookback_days": 180,
            "holding_cost": 0.05,
            "stockout_cost": 1.0,
        },
    },
    "restaurant": {
        "name": "Restaurant Inventory",
        "description": "Forecast food inventory needs",
        "sample_data_url": "https://.../restaurant-sample.csv",
        "recommended_config": {
            "train_lookback_days": 90,
            "holding_cost": 0.2,
            "stockout_cost": 2.0,
        },
    },
}


KNOWLEDGE_BASE_ARTICLES = {
    "getting_started": {
        "title": "Getting Started with HorizonCast",
        "content": """
# Getting Started

1. **Create Account**: Sign up at horizoncast.com
2. **Set API Key**: Generate API key in settings
3. **Upload Data**: Use web UI or API to upload CSV
4. **Train Model**: Configure and start training
5. **Make Predictions**: Use trained model for forecasting

## Required Data Format

Your CSV should include:
- `date`: Date column (YYYY-MM-DD format)
- `sales` or `demand`: Target to forecast
- `store_id`, `item_id`: Grouping dimensions
- Optional: `price`, `event`, `weather`, etc.

## Typical Workflow

```python
from horizoncast import HorizonCast

client = HorizonCast(api_key="your-key")
dataset = client.datasets.upload("sales.csv")
run = client.forecasts.train(dataset_id=dataset.id)
pred = client.forecasts.predict(run_id=run.id, data={...})
```
""",
    },
    "data_preparation": {
        "title": "Preparing Your Data",
        "content": """
# Data Preparation Guide

## Required Columns

- **date**: ISO 8601 format (YYYY-MM-DD)
- **target**: Sales/demand to forecast
- **store_id**: Store/location identifier
- **item_id**: Product identifier

## Optional Enriching Features

- **price**: Product price
- **promo**: Promotion flag
- **weather**: Weather conditions
- **events**: Special events or holidays

## Data Quality Checks

1. No missing dates (use interpolation if needed)
2. No null values in date/target
3. Date range should be at least 1 year for good models
4. Remove outliers if they're errors

## Example CSV

```
date,store_id,item_id,sales,price
2024-01-01,1,100,50,9.99
2024-01-02,1,100,52,9.99
...
```
""",
    },
    "uncertainty_intervals": {
        "title": "Understanding Uncertainty Intervals",
        "content": """
# Uncertainty Intervals Explained

HorizonCast uses conformal prediction to provide calibrated uncertainty intervals.

## What are Confidence Intervals?

A 90% confidence interval means: "We are 90% confident the true value lies between the lower and upper bounds."

## Interpreting Results

- **Point forecast**: Best guess for the value
- **Lower bound**: Pessimistic scenario (low demand)
- **Upper bound**: Optimistic scenario (high demand)
- **Interval width**: Measure of uncertainty

## Example

Forecast: 100 units
90% CI: [85, 115]

This means there's a 90% chance actual demand will be between 85-115 units.

## Use Cases

- **Inventory planning**: Use upper bound to avoid stockouts
- **Cost analysis**: Use lower bound for conservative projections
- **Risk assessment**: Wider intervals = more uncertainty
""",
    },
}


def get_onboarding_progress(completed_steps: list[str]) -> dict:
    """Calculate onboarding progress."""
    total = len(ONBOARDING_FLOW)
    completed = len([s for s in ONBOARDING_FLOW if s.id in completed_steps])
    return {
        "progress_percent": (completed / total) * 100,
        "completed": completed,
        "total": total,
        "next_step": next((s for s in ONBOARDING_FLOW if s.id not in completed_steps), None),
    }
