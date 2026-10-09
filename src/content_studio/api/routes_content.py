"""Content item and revision API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from content_studio.models.content import (
    ContentType,
    ContentStatus,
    ContentItem,
    ContentItemCreate,
    ContentItemUpdate,
    ContentRevision,
)
from content_studio.database.repository import ContentStudioRepository
from content_studio.api.dependencies import get_repo

router = APIRouter(prefix="/content", tags=["Content"])


@router.post("", response_model=ContentItem, status_code=201)
async def create_content_item(
    payload: ContentItemCreate, repo: ContentStudioRepository = Depends(get_repo)
):
    project = await repo.get_project(payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await repo.create_content_item(payload)


@router.get("", response_model=List[ContentItem])
async def list_content_items(
    project_id: Optional[int] = Query(None, description="Filter by project"),
    content_type: Optional[ContentType] = Query(None, description="Filter by content channel"),
    status: Optional[ContentStatus] = Query(None, description="Filter by publication status"),
    search: Optional[str] = Query(None, description="Keyword search in title or body"),
    repo: ContentStudioRepository = Depends(get_repo),
):
    return await repo.get_content_items(
        project_id=project_id,
        content_type=content_type,
        status=status,
        search=search,
    )


@router.get("/{content_id}", response_model=ContentItem)
async def get_content_item(content_id: int, repo: ContentStudioRepository = Depends(get_repo)):
    item = await repo.get_content_item(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    return item


@router.patch("/{content_id}", response_model=ContentItem)
async def update_content_item(
    content_id: int, payload: ContentItemUpdate, repo: ContentStudioRepository = Depends(get_repo)
):
    updated = await repo.update_content_item(content_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Content item not found")
    return updated


@router.delete("/{content_id}", status_code=204)
async def delete_content_item(content_id: int, repo: ContentStudioRepository = Depends(get_repo)):
    deleted = await repo.delete_content_item(content_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Content item not found")
    return None


@router.get("/{content_id}/revisions", response_model=List[ContentRevision])
async def get_content_revisions(content_id: int, repo: ContentStudioRepository = Depends(get_repo)):
    item = await repo.get_content_item(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    return await repo.get_revisions(content_id)
