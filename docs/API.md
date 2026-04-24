"""API Documentation and Usage Guide."""

# HorizonCast REST API

## Authentication

All API requests require an API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "healthy"
}
```

### Datasets

#### Upload Dataset

```http
POST /api/datasets/upload
Content-Type: application/json

{
  "name": "Q4 Sales Data",
  "description": "Sales for Q4 2024",
  "file_key": "s3://bucket/data.csv",
  "row_count": 1000000,
  "columns": ["date", "store_id", "sales", "price"]
}
```

#### List Datasets

```http
GET /api/datasets/
Authorization: Bearer YOUR_API_KEY
```

#### Get Dataset

```http
GET /api/datasets/{dataset_id}
Authorization: Bearer YOUR_API_KEY
```

### Forecasting

#### Start Training

```http
POST /api/forecasts/train
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "dataset_id": "ds_abc123",
  "train_end_date": "2025-01-01",
  "val_end_date": "2025-02-01",
  "holding_cost": 0.1,
  "stockout_cost": 0.5,
  "include_embeddings": false
}
```

Response:
```json
{
  "run_id": "run_xyz789",
  "job_id": "job_abc123"
}
```

#### Get Training Run

```http
GET /api/forecasts/runs/{run_id}
Authorization: Bearer YOUR_API_KEY
```

Response:
```json
{
  "run_id": "run_xyz789",
  "dataset_id": "ds_abc123",
  "status": "completed",
  "metrics": {
    "test_rmse": 1.6646,
    "test_mae": 0.8783,
    "test_coverage": 0.8983
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Make Prediction

```http
POST /api/forecasts/predict
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "run_id": "run_xyz789",
  "data": {
    "lag_7": 100.5,
    "lag_14": 102.3,
    "price": 9.99
  }
}
```

Response:
```json
{
  "prediction": 105.2,
  "lower_bound": 102.1,
  "upper_bound": 108.3,
  "confidence": 0.9
}
```

#### Get Model Explanation

```http
GET /api/forecasts/runs/{run_id}/explain
Authorization: Bearer YOUR_API_KEY
```

Response:
```json
{
  "feature_importance": {
    "lag_7": 0.35,
    "lag_14": 0.25,
    "price": 0.20
  },
  "top_features": [
    ["lag_7", 0.35],
    ["lag_14", 0.25]
  ],
  "shap_available": true
}
```

## Error Handling

All errors return JSON with status and message:

```json
{
  "detail": "Invalid API key"
}
```

Common status codes:
- `200`: Success
- `400`: Bad request
- `401`: Unauthorized
- `404`: Not found
- `500`: Server error

## Rate Limiting

API key limits per tier:
- **Starter**: 100 requests/minute
- **Professional**: 1000 requests/minute
- **Enterprise**: Custom

## Webhooks

Subscribe to event notifications:

```http
POST /api/webhooks/subscribe
Content-Type: application/json

{
  "event": "training.completed",
  "url": "https://your-app.com/webhook"
}
```

Events:
- `training.started`
- `training.completed`
- `training.failed`
- `prediction.made`

## SDKs

### Python

```python
from horizoncast import HorizonCast

client = HorizonCast(api_key="your_api_key")

# Upload dataset
dataset = client.datasets.upload("data.csv", name="Sales Data")

# Start training
run = client.forecasts.train(dataset_id=dataset.id)

# Wait for completion
result = client.forecasts.wait(run.id)

# Make prediction
pred = client.forecasts.predict(
    run_id=run.id,
    data={"lag_7": 100, "price": 9.99}
)

print(f"Prediction: {pred.value} ± {pred.interval_width}")
```

### JavaScript/Node.js

```javascript
import { HorizonCast } from "horizoncast-js"

const client = new HorizonCast({ apiKey: "your_api_key" })

// Upload and train
const dataset = await client.datasets.upload("data.csv")
const run = await client.forecasts.train({
  datasetId: dataset.id,
})

// Make prediction
const pred = await client.forecasts.predict({
  runId: run.id,
  data: { lag_7: 100, price: 9.99 },
})

console.log(`Prediction: ${pred.value}`)
```

## OpenAPI Specification

Access at: `http://localhost:8000/openapi.json`

API documentation at: `http://localhost:8000/docs`
