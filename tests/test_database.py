"""Tests for ContentStudioRepository."""

import pytest
from content_studio.models.project import ProjectCreate, ProjectUpdate
from content_studio.models.content import (
    ContentType,
    ContentStatus,
    Tone,
    ContentItemCreate,
    ContentItemUpdate,
)
from content_studio.database.repository import ContentStudioRepository


@pytest.mark.asyncio
async def test_project_crud(test_repo: ContentStudioRepository):
    # Create
    proj = await test_repo.create_project(
        ProjectCreate(name="Q4 Marketing Campaign", description="Launch strategy")
    )
    assert proj.id is not None
    assert proj.name == "Q4 Marketing Campaign"

    # Get
    fetched = await test_repo.get_project(proj.id)
    assert fetched is not None
    assert fetched.id == proj.id

    # List
    all_p = await test_repo.get_projects()
    assert len(all_p) >= 1

    # Update
    updated = await test_repo.update_project(
        proj.id, ProjectUpdate(name="Q4 Campaign Updated")
    )
    assert updated.name == "Q4 Campaign Updated"

    # Delete
    deleted = await test_repo.delete_project(proj.id)
    assert deleted is True
    assert await test_repo.get_project(proj.id) is None
    assert await test_repo.delete_project(999999) is False
    assert await test_repo.update_project(999999, ProjectUpdate(name="None")) is None


@pytest.mark.asyncio
async def test_content_lifecycle_and_revisions(test_repo: ContentStudioRepository):
    proj = await test_repo.create_project(ProjectCreate(name="Dev Blog"))

    # Create item
    item = await test_repo.create_content_item(
        ContentItemCreate(
            project_id=proj.id,
            title="Building Async APIs in Python",
            body="This is the first draft of our comprehensive guide on async systems.",
            content_type=ContentType.BLOG,
            tags=["python", "async"],
            tone=Tone.TECHNICAL,
        )
    )
    assert item.id is not None
    assert item.status == ContentStatus.DRAFT
    assert item.word_count > 5
    assert len(item.tags) == 2

    # Check revision 1
    revs = await test_repo.get_revisions(item.id)
    assert len(revs) == 1
    assert revs[0].revision_number == 1
    assert revs[0].body == item.body

    # Update body -> triggers revision 2
    updated = await test_repo.update_content_item(
        item.id,
        ContentItemUpdate(
            body="This is the updated second revision with enhanced code examples.",
            status=ContentStatus.REVIEW,
        ),
    )
    assert updated.status == ContentStatus.REVIEW
    assert "second revision" in updated.body

    revs_after = await test_repo.get_revisions(item.id)
    assert len(revs_after) == 2
    assert revs_after[1].revision_number == 2

    # Filter items
    items = await test_repo.get_content_items(
        project_id=proj.id,
        content_type=ContentType.BLOG,
        status=ContentStatus.REVIEW,
    )
    assert len(items) == 1
    assert items[0].id == item.id

    # Search
    search_res = await test_repo.get_content_items(search="enhanced")
    assert len(search_res) == 1


@pytest.mark.asyncio
async def test_analytics_summary(test_repo: ContentStudioRepository):
    proj = await test_repo.create_project(ProjectCreate(name="Analytics Test"))

    await test_repo.create_content_item(
        ContentItemCreate(
            project_id=proj.id,
            title="Post 1",
            body="Short tweet draft.",
            content_type=ContentType.TWEET,
        )
    )
    i2 = await test_repo.create_content_item(
        ContentItemCreate(
            project_id=proj.id,
            title="Post 2",
            body="Longer article with multiple words for testing analytics aggregation.",
            content_type=ContentType.BLOG,
        )
    )
    await test_repo.update_content_item(i2.id, ContentItemUpdate(status=ContentStatus.PUBLISHED))

    summary = await test_repo.get_analytics_summary(proj.id)
    assert summary["project_id"] == proj.id
    assert summary["total_items"] == 2
    assert summary["total_words"] > 0
    assert summary["status_distribution"]["published"] == 1
    assert summary["status_distribution"]["draft"] == 1
    assert summary["channel_distribution"]["tweet"] == 1
    assert summary["channel_distribution"]["blog"] == 1
