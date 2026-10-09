"""Cross-Channel Content Repurposer Engine."""

import logging
from typing import List, Optional
from content_studio.config import Settings
from content_studio.models.content import ContentType, Tone
from content_studio.models.generation import (
    RepurposeRequest,
    RepurposeResponse,
    RepurposeItem,
)
from content_studio.engine.social_generator import SocialGenerator
from content_studio.engine.video_script_generator import VideoScriptGenerator

logger = logging.getLogger(__name__)


class ContentRepurposer:
    """Transforms single source text into a suite of multi-platform assets."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.social_gen = SocialGenerator(settings)
        self.video_gen = VideoScriptGenerator(settings)

    async def repurpose(self, request: RepurposeRequest) -> RepurposeResponse:
        """Repurpose input text into selected or all target channel formats."""
        source_text = request.source_text.strip()
        target_types = request.target_types or [
            ContentType.TWEET,
            ContentType.LINKEDIN,
            ContentType.INSTAGRAM,
            ContentType.TELEGRAM,
            ContentType.VIDEO_SCRIPT,
        ]

        # Extract theme or title from first line
        first_line = source_text.split("\n")[0].replace("#", "").strip()
        topic = first_line[:60] if first_line else "Core Strategy"

        items: List[RepurposeItem] = []

        for c_type in target_types:
            if c_type == ContentType.VIDEO_SCRIPT:
                res = await self.video_gen.generate(topic=topic, tone=request.tone)
            else:
                res = await self.social_gen.generate(
                    topic=topic, content_type=c_type, tone=request.tone
                )

            items.append(
                RepurposeItem(
                    content_type=c_type,
                    title=res.title,
                    body=res.body,
                    char_count=len(res.body),
                )
            )

        logger.info(
            f"Repurposed source text ({len(source_text)} chars) into {len(items)} channel formats."
        )

        return RepurposeResponse(
            source_length=len(source_text),
            items=items,
        )
