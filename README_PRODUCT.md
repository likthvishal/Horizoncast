# HorizonCast - Production-Grade Demand Forecasting Platform

**Transform demand forecasting into strategic competitive advantage with AI-driven uncertainty quantification.**

## What is HorizonCast?

HorizonCast is an end-to-end demand forecasting system combining:
- **Classical time-series features** (lags, rolling stats, calendar effects)
- **LLM-enriched semantic embeddings** (product/event context)
- **LightGBM forecasting** with early stopping
- **Conformal prediction intervals** for calibrated uncertainty
- **Business-aware inventory cost evaluation** (stockout vs holding)
- **Production ML architecture** designed for scale

## Products

HorizonCast is available in three deployment models:

### 1. SaaS (Cloud Hosted)
- **URL**: https://horizoncast.io
- **No setup required** - start forecasting in minutes
- **Pricing**: Starter ($199/mo), Professional ($999/mo), Enterprise (custom)
- **Auto-scaling**, managed database, SSL/TLS included

### 2. Self-Hosted (Docker Compose)
- **For enterprises** needing on-premise deployment
- **Your infrastructure** - full control and compliance
- **Setup**: `docker-compose up -d`
- **Support**: Professional support packages available

### 3. API-Only (Serverless)
- **Integrate into your app** with REST API
- **Pay-per-prediction** or monthly caps
- **SDKs**: Python, JavaScript/TypeScript, cURL
- **Perfect for**: B2B integrations, white-label solutions

## Quick Start

### Option A: Cloud (SaaS)
```
1. Visit https://horizoncast.io
2. Sign up with email
3. Upload CSV file
4. Start training
5. Get predictions + intervals
```

### Option B: Self-Hosted
```bash
git clone https://github.com/horizoncast/horizoncast
cd horizoncast
docker-compose up -d
# Access at http://localhost:3000
```

### Option C: API
```python
from horizoncast import HorizonCast

client = HorizonCast(api_key="your-key")
dataset = client.datasets.upload("sales.csv")
run = client.forecasts.train(dataset_id=dataset.id)
predictions = client.forecasts.predict(run_id=run.id, data={...})
```

## Features

### Core Capabilities
- ✅ **Hybrid ML**: Classical + LLM-enriched features
- ✅ **Uncertainty Quantification**: Conformal prediction intervals (90%+ coverage)
- ✅ **Business Metrics**: Inventory cost, RMSE, MAE, pinball loss
- ✅ **Explainability**: SHAP feature importance, model interpretation
- ✅ **Batch Predictions**: Upload CSV → get forecasts with intervals
- ✅ **Scheduled Retraining**: Auto-retrain on new data
- ✅ **Webhooks**: Event-driven notifications
- ✅ **Audit Logging**: Complete compliance tracking

### Enterprise
- ✅ **Multi-Tenancy**: Isolated customer data
- ✅ **Role-Based Access**: Admin, Analyst, Viewer
- ✅ **API Rate Limiting**: Tier-based usage controls
- ✅ **SLA Monitoring**: Uptime and performance tracking
- ✅ **Custom Integrations**: REST API + SDKs
- ✅ **Dedicated Support**: Professional support plans

## Architecture

```
┌─────────────────────────────────────┐
│  Customer Touchpoints               │
├─────────────────────────────────────┤
│ Web Dashboard | REST API | SDKs     │
└──────────────┬──────────────────────┘
               │
        ┌──────▼───────┐
        │ Auth & Auth0 │
        │ Multi-Tenant │
        └──────┬───────┘
               │
    ┌──────────┴──────────────┐
    │                         │
┌───▼────┐         ┌─────────▼──────┐
│Backend │         │  ML Pipeline   │
│FastAPI │         │  (LightGBM,    │
│        │         │   MAPIE,       │
└───┬────┘         │   Features)    │
    │              └─────────┬──────┘
    └──────────┬─────────────┘
               │
        ┌──────▼──────────┐
        │ PostgreSQL +    │
        │ S3/Blob Storage │
        └─────────────────┘
```

## Use Cases

### Retail & E-Commerce
**Optimize inventory levels, reduce stockouts, minimize excess holding**

### Supply Chain & Logistics
**Forecast demand, plan shipments, optimize warehouse capacity**

### Food & Restaurant
**Predict daily orders, manage perishable inventory, reduce waste**

### Consulting & Analytics Agencies
**White-label forecasting for your clients**

## Data Requirements

**Minimum**: 1 year of historical daily/weekly data
**Recommended**: 2-3 years with seasonal variation

```csv
date,store_id,item_id,sales,price
2024-01-01,1,100,50,9.99
2024-01-02,1,100,52,9.99
```

## Validated Performance

From production runs on M5 dataset:
- **Val RMSE**: 1.6646
- **Val MAE**: 0.8783
- **Test Coverage**: 89.83% (target: 90%)
- **Business Cost**: $0.2547 per unit

## Pricing

### Cloud (SaaS)

| Tier | Price | Datasets | Storage | API | Support |
|------|-------|----------|---------|-----|---------|
| **Starter** | $199/mo | 10 | 10GB | ✓ | Email |
| **Professional** | $999/mo | Unlimited | 100GB | ✓ | Priority |
| **Enterprise** | Custom | Unlimited | Custom | ✓ | Dedicated |

### Self-Hosted
- **License**: $2,000/year (single instance)
- **Support**: $500/month (professional support bundle)

### API (Pay-per-prediction)
- **Per prediction**: $0.01-$0.10
- **Monthly minimum**: $99
- **Volume discounts**: Available

## Documentation

- 📖 [Implementation Guide](./docs/IMPLEMENTATION.md)
- 🔌 [REST API Reference](./docs/API.md)
- 🔐 [Authentication Setup](./docs/AUTH_SETUP.md)
- 🐳 [Self-Hosted Guide](./docs/SELF_HOSTED.md)
- 🎓 [Customer Knowledge Base](./docs/KNOWLEDGE_BASE.md)

## Getting Help

- **API Docs**: `/docs` (OpenAPI/Swagger)
- **GitHub Issues**: [horizoncast/horizoncast/issues](https://github.com/horizoncast/horizoncast)
- **Community**: [Discuss](https://github.com/horizoncast/horizoncast/discussions)
- **Enterprise Support**: sales@horizoncast.io

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Cache**: Redis
- **ML**: LightGBM, MAPIE, scikit-learn, scikit-learn
- **Deployment**: Docker, Vercel Functions, Railway
- **Monitoring**: Prometheus, Grafana (optional)

### Frontend
- **Framework**: Next.js 14 (React 18)
- **UI**: Tailwind CSS, shadcn/ui
- **Auth**: Clerk
- **API Client**: Axios, React Query
- **Deployment**: Vercel

### SDKs
- **Python**: `pip install horizoncast`
- **JavaScript**: `npm install horizoncast-js`

## Roadmap

### Q2 2026
- [x] Core MVP (backend, frontend, API)
- [x] Multi-deployment options
- [x] Documentation & SDKs

### Q3 2026
- [ ] Time-series anomaly detection
- [ ] Advanced seasonality handling
- [ ] Custom feature engineering UI
- [ ] Integrations: Shopify, SAP, Oracle

### Q4 2026
- [ ] Graph neural networks for hierarchical forecasts
- [ ] Real-time streaming predictions
- [ ] AutoML hyperparameter tuning
- [ ] Mobile app (iOS/Android)

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

HorizonCast is available under dual licensing:
- **Community**: Open source (MIT license)
- **Enterprise**: Commercial license + support

## Contact

- **Website**: https://horizoncast.io
- **Email**: hello@horizoncast.io
- **Twitter**: @horizoncast_io
- **LinkedIn**: [HorizonCast](https://linkedin.com/company/horizoncast)

---

**Built for teams who care about forecast accuracy, uncertainty, and business impact.**

*Last updated: April 24, 2026*
