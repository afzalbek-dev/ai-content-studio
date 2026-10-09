"""Pytest fixtures for AI Content Studio test suite."""

import pytest
from pathlib import Path
from starlette.testclient import TestClient

from content_studio.config import Settings
from content_studio.database.repository import ContentStudioRepository
from content_studio.engine.repurposer import ContentRepurposer
from content_studio.app import create_app


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_content_studio.db"


@pytest.fixture
def test_settings(temp_db_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{temp_db_path}",
        app_env="testing",
        log_level="DEBUG",
        gemini_api_key=None,  # Offline deterministic engine for fast, reproducible tests
    )


@pytest.fixture
async def test_repo(temp_db_path: Path) -> ContentStudioRepository:
    repo = ContentStudioRepository(temp_db_path)
    await repo.init_db()
    return repo


@pytest.fixture
def test_repurposer(test_settings: Settings) -> ContentRepurposer:
    return ContentRepurposer(test_settings)


@pytest.fixture
def test_app(test_settings: Settings, test_repo: ContentStudioRepository, test_repurposer: ContentRepurposer):
    return create_app(
        settings=test_settings,
        repo=test_repo,
        repurposer=test_repurposer,
    )


@pytest.fixture
def client(test_app) -> TestClient:
    with TestClient(test_app) as c:
        yield c
