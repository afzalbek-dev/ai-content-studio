"""Content item and revision models."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ContentType(str, Enum):
    BLOG = "blog"
    TWEET = "tweet"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    VIDEO_SCRIPT = "video_script"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    VIRAL = "viral"
    TECHNICAL = "technical"
    WITTY = "witty"


class ContentItemCreate(BaseModel):
    project_id: int
    title: str = Field(min_length=3, max_length=250)
    body: str = Field(min_length=1)
    content_type: ContentType = ContentType.BLOG
    tags: List[str] = Field(default_factory=list)
    tone: Tone = Tone.PROFESSIONAL


class ContentItemUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    content_type: Optional[ContentType] = None
    status: Optional[ContentStatus] = None
    tags: Optional[List[str]] = None
    tone: Optional[Tone] = None


class ContentItem(BaseModel):
    id: int
    project_id: int
    title: str
    body: str
    content_type: ContentType
    status: ContentStatus = ContentStatus.DRAFT
    tone: Tone = Tone.PROFESSIONAL
    tags: List[str] = Field(default_factory=list)
    word_count: int = 0
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ContentRevision(BaseModel):
    id: int
    content_id: int
    revision_number: int
    body: str
    created_at: datetime = Field(default_factory=utc_now)
