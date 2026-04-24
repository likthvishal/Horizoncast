"""API routes for dataset management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import get_current_tenant
from backend.schemas import DatasetCreate, DatasetResponse
from datetime import datetime
from uuid import uuid4

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

# Placeholder in-memory store (replace with DB in production)
datasets_store: dict[str, DatasetResponse] = {}


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    dataset: DatasetCreate,
    tenant_id: str = Depends(get_current_tenant),
) -> DatasetResponse:
    """Upload and register a dataset."""
    dataset_id = str(uuid4())[:8]
    response = DatasetResponse(
        dataset_id=dataset_id,
        name=dataset.name,
        description=dataset.description,
        row_count=dataset.row_count,
        columns=dataset.columns,
        created_at=datetime.now(),
        file_key=dataset.file_key,
    )
    datasets_store[dataset_id] = response
    return response


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    tenant_id: str = Depends(get_current_tenant),
) -> DatasetResponse:
    """Get dataset metadata."""
    if dataset_id not in datasets_store:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets_store[dataset_id]


@router.get("/", response_model=list[DatasetResponse])
async def list_datasets(
    tenant_id: str = Depends(get_current_tenant),
) -> list[DatasetResponse]:
    """List all datasets."""
    return list(datasets_store.values())


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    tenant_id: str = Depends(get_current_tenant),
) -> dict[str, str]:
    """Delete a dataset."""
    if dataset_id not in datasets_store:
        raise HTTPException(status_code=404, detail="Dataset not found")
    del datasets_store[dataset_id]
    return {"message": "Dataset deleted"}
