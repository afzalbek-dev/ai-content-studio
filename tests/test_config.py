"""Tests for configuration settings."""

from pathlib import Path
from content_studio.config import Settings, get_settings


def test_settings_defaults():
    s = Settings()
    assert s.app_env in ("development", "production", "testing")
    assert s.port > 0
    assert s.gemini_model == "gemini-2.5-flash"
    assert s.database_url is not None


def test_sqlite_path_resolution(tmp_path: Path):
    db_file = tmp_path / "nested" / "studio.db"
    s = Settings(database_url=f"sqlite:///{db_file}")
    p = s.sqlite_path
    assert p == db_file
    assert p.parent.exists()


def test_cached_settings():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
