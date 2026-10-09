"""Video Script Generator for Short-form (Shorts/Reels/TikTok) and Long-form YouTube."""

import logging
from content_studio.config import Settings
from content_studio.models.content import ContentType, Tone
from content_studio.models.generation import GenerateResponse
from content_studio.engine.base import BaseGenerator

logger = logging.getLogger(__name__)


class VideoScriptGenerator(BaseGenerator):
    """Generates structured video production scripts with timing and visual cues."""

    async def generate(
        self,
        topic: str,
        tone: Tone = Tone.VIRAL,
        keywords: list = None,
    ) -> GenerateResponse:
        keywords = keywords or []
        kw_str = ", ".join(keywords) if keywords else "creator, viral, tips"

        if self.settings.gemini_api_key:
            try:
                system_prompt = (
                    f"You are a viral YouTube Shorts and Reels scriptwriter.\n"
                    f"Structure video scripts with precise time markers [0-3s], [3-15s], [15-45s], [45-60s] "
                    f"and visual cue instructions (e.g., [VISUAL: ...]). Tone: {tone.value}."
                )
                prompt = f"Write a 60-second high-retention video script about '{topic}'."
                body = await self._call_gemini_api(prompt, system_prompt)
                return GenerateResponse(
                    topic=topic,
                    content_type=ContentType.VIDEO_SCRIPT,
                    tone=tone,
                    title=f"Shorts Script: {topic.title()}",
                    body=body,
                    metadata={"duration": "60s", "format": "9:16 vertical"},
                )
            except Exception as e:
                logger.warning(f"Video script generation failed with Gemini ({e}), falling back to offline.")

        return self._generate_offline(topic, tone, keywords)

    def _generate_offline(self, topic: str, tone: Tone, keywords: list) -> GenerateResponse:
        title = f"Viral 60s Script: {topic.title()}"
        script_body = f"""# 🎬 VIDEO SCRIPT: {topic.title()}
Format: Vertical Video (9:16) | Target Duration: 55-60 Seconds | Tone: {tone.value.upper()}

---

### [00:00 - 00:03] 🔥 THE HOOK
[VISUAL: Fast zoom-in on presenter with bold animated text on screen: "STOP DOING THIS!"]
**PRESENTER (High energy):**
"If you are still struggling with {topic}, you are making one critical mistake that is costing you hours!"

---

### [00:03 - 00:15] ⚠️ THE PROBLEM / TENSION
[VISUAL: Screen recording showing frustration or cluttered screen / sound effect: buzzer]
**PRESENTER:**
"Most people try to jump straight to the end result without setting up the fundamentals. But here is the truth: without a clean system, everything breaks under pressure."

---

### [00:15 - 00:45] 💡 THE SOLUTION & 3 STEPS
[VISUAL: Clean 3-step diagram animation on screen with chime sound]
**PRESENTER:**
"Here is how you actually fix it in 3 steps:
Step 1: Simplify your workflow to only the highest leverage actions.
Step 2: Automate repetitive tasks using modern AI tools.
Step 3: Test and measure your output every single week."

---

### [00:45 - 00:60] 🚀 CALL TO ACTION (CTA)
[VISUAL: Presenter smiling, pointing down to follow button / on-screen graphic: 'FOLLOW FOR MORE']
**PRESENTER:**
"Try this today and see the difference immediately! Save this video so you don't lose it, and follow for more daily breakdowns!"
"""
        return GenerateResponse(
            topic=topic,
            content_type=ContentType.VIDEO_SCRIPT,
            tone=tone,
            title=title,
            body=script_body,
            metadata={
                "duration": "60s",
                "format": "9:16 vertical",
                "engine": "deterministic-offline",
            },
        )
