"""Tests for content generators."""

import pytest
from content_studio.config import Settings
from content_studio.models.content import ContentType, Tone
from content_studio.engine.blog_generator import BlogGenerator
from content_studio.engine.social_generator import SocialGenerator
from content_studio.engine.video_script_generator import VideoScriptGenerator


@pytest.fixture
def gen_settings() -> Settings:
    return Settings(gemini_api_key=None)


@pytest.mark.asyncio
async def test_blog_generator(gen_settings: Settings):
    gen = BlogGenerator(gen_settings)
    res = await gen.generate(
        topic="Microservices Architecture",
        tone=Tone.TECHNICAL,
        target_audience="Backend Developers",
        keywords=["docker", "kubernetes", "scalability"],
    )

    assert res.content_type == ContentType.BLOG
    assert "Microservices Architecture" in res.title
    assert "Meta Description" in res.body
    assert "Executive Summary" in res.body
    assert "Call to Action" in res.body
    assert int(res.metadata["word_count"]) > 50


@pytest.mark.asyncio
async def test_social_generator_channels(gen_settings: Settings):
    gen = SocialGenerator(gen_settings)

    # Tweet / Thread
    tw = await gen.generate("Clean Code Principles", ContentType.TWEET, Tone.VIRAL)
    assert "🧵 1/4" in tw.body
    assert "#CleanCodePrinciples" in tw.body

    # LinkedIn
    li = await gen.generate("Clean Code Principles", ContentType.LINKEDIN, Tone.PROFESSIONAL)
    assert "Most leaders talk about" in li.body
    assert "Agree or disagree?" in li.body

    # Instagram
    ig = await gen.generate("Clean Code Principles", ContentType.INSTAGRAM, Tone.CONVERSATIONAL)
    assert "✨" in ig.body
    assert "Save this post" in ig.body

    # Telegram
    tg = await gen.generate("Clean Code Principles", ContentType.TELEGRAM, Tone.PROFESSIONAL)
    assert "🔥" in tg.body
    assert "Aniq arxitektura" in tg.body or "Qo'llanma" in tg.body


@pytest.mark.asyncio
async def test_video_script_generator(gen_settings: Settings):
    gen = VideoScriptGenerator(gen_settings)
    script = await gen.generate("AI Productivity Hacks", Tone.VIRAL)

    assert script.content_type == ContentType.VIDEO_SCRIPT
    assert "[00:00 - 00:03]" in script.body
    assert "[00:45 - 00:60]" in script.body
    assert "[VISUAL:" in script.body
    assert "PRESENTER" in script.body
