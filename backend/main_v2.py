"""Enhanced main.py with auth and tenant middleware."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api_datasets import router as datasets_router
from backend.api_forecast import router as forecast_router
from backend.middleware.tenant import TenantIsolationMiddleware, AuditLoggingMiddleware

app = FastAPI(
    title="HorizonCast API",
    description="Production-grade demand forecasting with uncertainty quantification",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(AuditLoggingMiddleware)
app.add_middleware(TenantIsolationMiddleware)

app.include_router(datasets_router)
app.include_router(forecast_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "HorizonCast API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
