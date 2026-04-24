"""File upload handling for datasets."""

from __future__ import annotations

import io
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException

from backend.auth import get_current_tenant

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Placeholder storage (use S3/Blob in production)
UPLOAD_DIR = Path("/tmp/horizoncast-uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_csv(content: bytes) -> tuple[bool, str | None, list[str] | None]:
    """Validate CSV file and extract headers."""
    try:
        text = content.decode("utf-8")
        lines = text.split("\n")
        if not lines:
            return False, "Empty file", None

        headers = [h.strip() for h in lines[0].split(",")]
        return True, None, headers
    except Exception as e:
        return False, str(e), None


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_current_tenant),
) -> dict[str, any]:
    """Upload a CSV file with validation."""
    if file.content_type not in ["text/csv", "application/csv"]:
        raise HTTPException(status_code=400, detail="File must be CSV format")

    try:
        content = await file.read()
        is_valid, error, headers = validate_csv(content)

        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {error}")

        # Save file (in production, upload to S3/Blob)
        file_path = UPLOAD_DIR / f"{tenant_id}_{file.filename}"
        file_path.write_bytes(content)

        # Count rows (excluding header)
        text = content.decode("utf-8")
        row_count = len(text.strip().split("\n")) - 1

        return {
            "filename": file.filename,
            "size_bytes": len(content),
            "row_count": row_count,
            "columns": headers,
            "file_key": str(file_path),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
