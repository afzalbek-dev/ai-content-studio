"""Tests for Content Repurposer engine."""

import pytest
from content_studio.config import Settings
from content_studio.models.content import ContentType, Tone
from content_studio.models.generation import RepurposeRequest
from content_studio.engine.repurposer import ContentRepurposer


@pytest.fixture
def repurposer() -> ContentRepurposer:
    return ContentRepurposer(Settings(gemini_api_key=None))


@pytest.mark.asyncio
async def test_full_repurpose(repurposer: ContentRepurposer):
    source_article = """# 10 Best Practices for Building Fault-Tolerant Distributed Systems

Distributed systems require defensive architecture, circuit breakers, idempotency tokens, and continuous observability.
Here is the practical roadmap to achieve high availability and low latency.
"""
    req = RepurposeRequest(
        source_text=source_article,
        tone=Tone.PROFESSIONAL,
    )
    result = await repurposer.repurpose(req)

    assert result.source_length == len(source_article.strip())
    assert len(result.items) == 5

    channels = [item.content_type for item in result.items]
    assert ContentType.TWEET in channels
    assert ContentType.LINKEDIN in channels
    assert ContentType.INSTAGRAM in channels
    assert ContentType.TELEGRAM in channels
    assert ContentType.VIDEO_SCRIPT in channels


@pytest.mark.asyncio
async def test_targeted_repurpose(repurposer: ContentRepurposer):
    req = RepurposeRequest(
        source_text="Mastering FastAPI Dependency Injection and Lifespan Events in 2026",
        target_types=[ContentType.TWEET, ContentType.LINKEDIN],
        tone=Tone.TECHNICAL,
    )
    result = await repurposer.repurpose(req)

    assert len(result.items) == 2
    types = [item.content_type for item in result.items]
    assert types == [ContentType.TWEET, ContentType.LINKEDIN]
