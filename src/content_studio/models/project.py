"""Project and Campaign models."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Project(BaseModel):
    id: int
    name: str
    description: str = ""
    created_at: datetime = Field(default_factory=utc_now)
