"""Study set CRUD routes."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import StudySetDetailResponse, StudySetResponse
from study_guide.database.operations import DatabaseOperations

router = APIRouter()


@router.get("/", response_model=list[StudySetResponse])
def list_study_sets(db: Session = Depends(get_db)):
    """List all study sets."""
    ops = DatabaseOperations(db)
    sets = ops.get_all_study_sets()
    return [
        StudySetResponse(
            id=s.id,
            set_type=s.set_type,
            title=s.title,
            item_count=s.item_count,
            document_id=s.document_id,
            created_at=s.created_at,
        )
        for s in sets
    ]


@router.get("/{study_set_id}", response_model=StudySetDetailResponse)
def get_study_set(study_set_id: int, db: Session = Depends(get_db)):
    """Get a study set with its full content."""
    ops = DatabaseOperations(db)
    study_set = ops.get_study_set(study_set_id)
    if study_set is None:
        raise HTTPException(status_code=404, detail=f"Study set {study_set_id} not found")
    content = json.loads(study_set.content_json)
    return StudySetDetailResponse(
        id=study_set.id,
        set_type=study_set.set_type,
        title=study_set.title,
        item_count=study_set.item_count,
        document_id=study_set.document_id,
        created_at=study_set.created_at,
        content=content,
    )


@router.delete("/{study_set_id}")
def delete_study_set(study_set_id: int, db: Session = Depends(get_db)):
    """Delete a study set."""
    ops = DatabaseOperations(db)
    deleted = ops.delete_study_set(study_set_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Study set {study_set_id} not found")
    return {"detail": f"Study set {study_set_id} deleted"}
