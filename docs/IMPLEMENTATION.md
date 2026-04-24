"""
# HorizonCast Implementation Guide

## Overview

HorizonCast has been transformed from a local ML prototype into a production-grade, multi-deployment demand forecasting platform. This guide covers all components and their integration.

## Phase 1: Backend Unification (COMPLETED)

### 1.1 Data Module
- **Files**: `horizoncast/data/download.py`, `horizoncast/data/preprocess.py`
- **Purpose**: Ingest raw M5 CSVs and create train/val/test splits
- **Usage**:
  ```bash
  python -m horizoncast.data.download --raw-dir data/raw --out data/processed/m5_merged.parquet
  python -m horizoncast.data.preprocess --in data/processed/m5_merged.parquet --out-dir data/processed/splits
  ```

### 1.2 Core ML Service
- **Files**: `horizoncast/core/pipeline.py`, `horizoncast/core/config.py`, `horizoncast/core/artifacts.py`
- **ForecastingService**: Unified API for train/predict/evaluate with versioned artifacts
- **Usage**:
  ```python
  from horizoncast.core.pipeline import ForecastingService
  from horizoncast.core.config import PipelineConfig
  
  service = ForecastingService(PipelineConfig())
  metrics = service.train(train_df, val_df)
  predictions_df, intervals = service.predict(test_df)
  ```

### 1.3 FastAPI Backend
- **Files**: `backend/main.py`, `backend/api_*.py`, `backend/jobs.py`
- **Endpoints**:
  - `/api/datasets/` - Dataset management (upload, list, delete)
  - `/api/forecasts/` - Training and predictions
  - `/api/upload/csv` - File upload with validation
- **Features**: Async job queue, structured logging, error handling

### 1.4 Database Layer
- **Files**: `backend/database/models.py`, `backend/database/crud.py`
- **Tables**: Tenants, Datasets, TrainingRuns, Predictions, AuditLogs, APIKeys
- **Migrations**: Use Alembic (create migration: `alembic revision --autogenerate -m "message"`)

## Phase 2: Frontend & UX (COMPLETED)

### 2.1 Next.js SaaS Frontend
- **Tech**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Structure**:
  - `frontend/app/` - Pages (dashboard, datasets, models, settings)
  - `frontend/components/` - Reusable components
  - `frontend/lib/` - API client and utilities
  - `frontend/hooks/` - React Query hooks for data fetching

### 2.2 Authentication & Multi-Tenancy
- **Clerk Integration**: `/docs/AUTH_SETUP.md`
- **RBAC**: Admin, Analyst, Viewer roles
- **Tenant Isolation**: Request middleware enforces tenant context
- **Middleware**: `backend/middleware/tenant.py`, `backend/middleware/auth.py`

### 2.3 Enhanced File Uploader
- **Features**: 
  - Drag-and-drop CSV/Parquet upload
  - Data preview (first N rows)
  - File validation (size, format, schema)
  - Progress indicators

## Phase 3: Deployment (COMPLETED)

### 3.1 SaaS Deployment (Vercel)
- **Frontend**: Deploy Next.js to Vercel (automatic from main branch)
- **Backend**: Deploy FastAPI to Vercel Functions or external PaaS
- **Database**: Vercel Postgres
- **Storage**: Vercel Blob or S3
- **Config**: `vercel.json`
- **CI/CD**: `.github/workflows/deploy.yml`

### 3.2 Self-Hosted (Docker Compose)
- **Services**: PostgreSQL, Redis, Backend (FastAPI), Frontend (Node.js), Nginx
- **Start**: `docker-compose up -d`
- **Docs**: `docs/SELF_HOSTED.md`
- **Backups**: `docker-compose exec postgres pg_dump ...`

### 3.3 API-Only Deployment
- **REST API** fully documented with OpenAPI/Swagger
- **SDKs**: Python, JavaScript/TypeScript
- **Scalable**: Run on Railway, Fly.io, Render, or AWS

## Phase 4: Enterprise Features (COMPLETED)

### 4.1 Scheduled Retraining
- **Task**: `backend/tasks/retraining.py`
- **Trigger**: Celery Beat for periodic retraining
- **Config**: Interval, hyperparameters, auto-promotion

### 4.2 Webhooks & Alerts
- **Events**: training.started, training.completed, training.failed, prediction.made
- **Manager**: `backend/webhooks.py`
- **Use**: Real-time notifications to customer systems

### 4.3 Observability
- **Logging**: `backend/observability.py` - Structured JSON logs
- **Tracing**: Simple APM tracer for performance monitoring
- **Health Checks**: `backend/health.py` - System and SLA monitoring

### 4.4 Customer Onboarding
- **Flow**: 5-step guided onboarding (account → upload → train → predict → explore)
- **Templates**: Pre-built configs for retail, e-commerce, restaurant
- **Knowledge Base**: How-to articles and troubleshooting

## SDKs

### Python SDK
```python
from horizoncast import HorizonCast

client = HorizonCast(api_url="http://localhost:8000", api_key="your-key")
dataset = client.datasets.upload("data.csv", name="Q4 Sales")
run = client.forecasts.train(dataset_id=dataset.id)
run = client.forecasts.wait(run.id)
pred = client.forecasts.predict(run_id=run.id, data={"lag_7": 100})
```

### JavaScript SDK
```javascript
import { HorizonCast } from "horizoncast-js"

const client = new HorizonCast()
const result = await client.startTraining({ datasetId: "ds_123" })
const run = await client.waitForTraining(result.runId)
const pred = await client.predict(run.runId, { lag_7: 100 })
```

## File Structure

```
horizoncast/
├── horizoncast/
│   ├── data/                  # [NEW] Data ingestion
│   ├── features/              # [EXISTING] Feature engineering
│   ├── models/                # [EXISTING] ML models
│   ├── evaluation/            # [EXISTING] Metrics
│   ├── core/                  # [NEW] ForecastingService, config, artifacts
│   └── dashboard/             # [LEGACY] Streamlit (kept for CLI)
├── backend/                   # [NEW] FastAPI REST API
│   ├── main.py
│   ├── api_*.py               # Route handlers
│   ├── database/              # SQLAlchemy models & CRUD
│   ├── middleware/            # Auth, tenant, audit
│   ├── tasks/                 # Celery tasks
│   ├── webhooks.py
│   ├── observability.py
│   ├── health.py
│   └── onboarding.py
├── frontend/                  # [NEW] Next.js React SaaS
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── hooks/
├── sdks/
│   ├── python-horizoncast/
│   └── js-horizoncast/
├── docs/
│   ├── API.md                 # API documentation
│   ├── AUTH_SETUP.md          # Auth configuration
│   ├── SELF_HOSTED.md         # Self-hosted guide
│   └── IMPLEMENTATION.md      # This file
├── docker-compose.yml         # [NEW] Self-hosted stack
├── Dockerfile.backend         # [NEW]
├── Dockerfile.frontend        # [NEW]
├── vercel.json                # [NEW] Vercel config
├── .github/workflows/         # [NEW] CI/CD
└── requirements.txt           # [UPDATED] Backend deps
```

## Deployment Checklist

### Pre-Launch
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] API keys and secrets secured
- [ ] Frontend build tested locally
- [ ] Backend health checks passing
- [ ] SSL/TLS certificates configured
- [ ] DNS records updated

### Launch
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to PaaS
- [ ] Run smoke tests (health check, simple training)
- [ ] Monitor error rates and performance
- [ ] Set up alerts for critical issues

### Post-Launch
- [ ] Customer onboarding flow tested
- [ ] Documentation up-to-date
- [ ] Support team trained
- [ ] Customer feedback collection started

## Next Steps

1. **Install Dependencies**: `pip install -r requirements.txt` (backend) + `npm install` (frontend)
2. **Configure Database**: Set `DATABASE_URL` environment variable
3. **Set Up Clerk**: Get API keys from https://dashboard.clerk.com
4. **Run Locally**:
   - Backend: `python backend/main.py` (or `python -m uvicorn backend.main:app --reload`)
   - Frontend: `cd frontend && npm run dev`
5. **Deploy**: Follow Vercel or self-hosted guides
6. **Monitor**: Set up logging and alerting

## Support

- API Docs: http://localhost:8000/docs
- GitHub Issues: https://github.com/horizoncast/horizoncast/issues
- Community Forum: https://community.horizoncast.io

---

**Implementation completed**: April 24, 2026
**Status**: Production-ready SaaS + self-hosted + API options
**Target customers**: Retail, supply chain, consultants
**First launch**: Q2 2026
"""
