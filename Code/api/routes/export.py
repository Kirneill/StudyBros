"""Study set export / file download route."""

import json
import re
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from api.dependencies import get_db
from study_guide.database.operations import DatabaseOperations
from study_guide.export.base import get_exporter

router = APIRouter()

_SUPPORTED_FORMATS = {"json", "anki", "markdown"}


@router.get("/{study_set_id}")
def export_study_set(
    study_set_id: int,
    format: str = Query(default="json", description="Export format: json, anki, markdown"),
    db: Session = Depends(get_db),
):
    """Export a study set as a downloadable file."""
    if format not in _SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{format}'. Must be one of: {', '.join(_SUPPORTED_FORMATS)}",
        )

    exporter = get_exporter(format)
    if exporter is None:
        raise HTTPException(status_code=400, detail=f"No exporter available for '{format}'")

    ops = DatabaseOperations(db)
    study_set = ops.get_study_set(study_set_id)
    if study_set is None:
        raise HTTPException(status_code=404, detail=f"Study set {study_set_id} not found")

    content = json.loads(study_set.content_json)
    ext = exporter.get_file_extension()
    raw_title = study_set.title or f"study_set_{study_set_id}"
    safe_title = re.sub(r"[^\w\-]", "_", raw_title)

    # Export to a temp directory so we don't litter the workspace
    tmp_dir = Path(tempfile.mkdtemp())
    output_path = tmp_dir / f"{safe_title}{ext}"

    result = exporter.export(content, output_path, title=study_set.title)
    if not result.success:
        raise HTTPException(status_code=500, detail=f"Export failed: {result.error}")

    return FileResponse(
        path=str(result.filepath),
        filename=f"{safe_title}{ext}",
        media_type="application/octet-stream",
        background=BackgroundTask(shutil.rmtree, tmp_dir, ignore_errors=True),
    )
