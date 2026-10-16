from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.category import CategoryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/categories", tags=["Learning Categories"])

@router.get("", response_model=List[CategoryResponse])
@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """
    Returns all active learning categories sorted by display order,
    including published tutorial counts.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.get_categories(db=db)
