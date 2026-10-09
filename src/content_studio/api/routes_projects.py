"""Project and Campaign API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from content_studio.models.project import Project, ProjectCreate, ProjectUpdate
from content_studio.database.repository import ContentStudioRepository
from content_studio.api.dependencies import get_repo

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=Project, status_code=201)
async def create_project(payload: ProjectCreate, repo: ContentStudioRepository = Depends(get_repo)):
    return await repo.create_project(payload)


@router.get("", response_model=List[Project])
async def list_projects(repo: ContentStudioRepository = Depends(get_repo)):
    return await repo.get_projects()


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: int, repo: ContentStudioRepository = Depends(get_repo)):
    project = await repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=Project)
async def update_project(
    project_id: int, payload: ProjectUpdate, repo: ContentStudioRepository = Depends(get_repo)
):
    updated = await repo.update_project(project_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, repo: ContentStudioRepository = Depends(get_repo)):
    deleted = await repo.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return None
