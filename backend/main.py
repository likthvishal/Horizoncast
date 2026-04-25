"""HorizonCast FastAPI backend application (demo-ready)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api_datasets import router as datasets_router
from backend.api_forecast import router as forecast_router
from backend.api_upload import router as upload_router

app = FastAPI(
    title="HorizonCast API",
    description="Production-grade demand forecasting with uncertainty quantification",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

import os
import re

_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://frontend-one-mauve-19.vercel.app",
]

_extra = os.getenv("CORS_ALLOW_ORIGINS", "")
if _extra:
    _default_origins.extend(o.strip() for o in _extra.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets_router)
app.include_router(forecast_router)
app.include_router(upload_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "service": "HorizonCast API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
