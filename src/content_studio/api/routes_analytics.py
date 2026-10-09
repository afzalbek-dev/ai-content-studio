"""Content Analytics and Studio Metrics API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query

from content_studio.database.repository import ContentStudioRepository
from content_studio.api.dependencies import get_repo

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_analytics_summary(
    project_id: Optional[int] = Query(None, description="Optional filter by project ID"),
    repo: ContentStudioRepository = Depends(get_repo),
):
    """Retrieve overall studio productivity, word counts, and channel breakdown."""
    return await repo.get_analytics_summary(project_id)
