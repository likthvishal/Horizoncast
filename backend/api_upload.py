"""File upload handling for datasets."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.auth import get_current_tenant

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = Path(tempfile.gettempdir()) / "horizoncast-uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_csv(content: bytes) -> tuple[bool, str | None, list[str] | None]:
    """Validate CSV file and extract headers."""
    try:
        text = content.decode("utf-8", errors="replace")
        lines = [line for line in text.split("\n") if line.strip()]
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
) -> dict[str, Any]:
    """Upload a CSV file with validation."""
    filename = file.filename or "upload.csv"
    if not (filename.endswith(".csv") or filename.endswith(".parquet")):
        raise HTTPException(
            status_code=400, detail="File must be CSV or Parquet"
        )

    try:
        content = await file.read()

        if filename.endswith(".csv"):
            is_valid, error, headers = validate_csv(content)
            if not is_valid:
                raise HTTPException(
                    status_code=400, detail=f"Invalid CSV: {error}"
                )
            text = content.decode("utf-8", errors="replace")
            row_count = len([line for line in text.split("\n") if line.strip()]) - 1
        else:
            headers = []
            row_count = 0

        safe_name = filename.replace("..", "_").replace("/", "_").replace("\\", "_")
        file_path = UPLOAD_DIR / f"{tenant_id}_{safe_name}"
        file_path.write_bytes(content)

        return {
            "filename": filename,
            "size_bytes": len(content),
            "row_count": row_count,
            "columns": headers,
            "file_key": str(file_path),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}") from e
