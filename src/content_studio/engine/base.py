"""Base Generator with Gemini API integration and deterministic offline fallback."""

import logging
from typing import Optional
import httpx

from content_studio.config import Settings

logger = logging.getLogger(__name__)


class BaseGenerator:
    """Base class for domain-specific AI generators."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def _call_gemini_api(self, prompt: str, system_prompt: str = "") -> str:
        """Execute Gemini API generation request."""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.settings.gemini_model}:generateContent"
            f"?key={self.settings.gemini_api_key}"
        )
        full_text = f"System Instructions: {system_prompt}\n\nTask: {prompt}"
        payload = {
            "contents": [{"parts": [{"text": full_text}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raise RuntimeError(f"Gemini API returned {resp.status_code}: {resp.text}")
