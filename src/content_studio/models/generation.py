"""Generation and Repurposing request and response schemas."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from content_studio.models.content import ContentType, Tone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    content_type: ContentType = ContentType.BLOG
    tone: Tone = Tone.PROFESSIONAL
    target_audience: Optional[str] = "General"
    keywords: List[str] = Field(default_factory=list)
    length_constraint: Optional[str] = "medium"  # short, medium, long


class GenerateResponse(BaseModel):
    topic: str
    content_type: ContentType
    tone: Tone
    title: str
    body: str
    metadata: Dict[str, str] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=utc_now)


class RepurposeRequest(BaseModel):
    source_text: str = Field(min_length=20)
    source_type: ContentType = ContentType.BLOG
    target_types: Optional[List[ContentType]] = None
    tone: Tone = Tone.CONVERSATIONAL


class RepurposeItem(BaseModel):
    content_type: ContentType
    title: str
    body: str
    char_count: int


class RepurposeResponse(BaseModel):
    source_length: int
    items: List[RepurposeItem]
    created_at: datetime = Field(default_factory=utc_now)
