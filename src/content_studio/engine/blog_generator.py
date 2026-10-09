"""Blog and Long-form Article Generator."""

import logging
from content_studio.config import Settings
from content_studio.models.content import Tone
from content_studio.models.generation import GenerateResponse, ContentType
from content_studio.engine.base import BaseGenerator

logger = logging.getLogger(__name__)


class BlogGenerator(BaseGenerator):
    """Generates structured SEO-optimized articles and blog posts."""

    async def generate(
        self,
        topic: str,
        tone: Tone = Tone.PROFESSIONAL,
        target_audience: str = "General",
        keywords: list = None,
        length_constraint: str = "medium",
    ) -> GenerateResponse:
        keywords = keywords or []
        kw_str = ", ".join(keywords) if keywords else "technology, innovation"

        if self.settings.gemini_api_key:
            try:
                system_prompt = (
                    f"You are an expert technical and editorial content writer.\n"
                    f"Generate a comprehensive, SEO-optimized blog post in Markdown format.\n"
                    f"Tone: {tone.value}. Target Audience: {target_audience}. Keywords: {kw_str}."
                )
                prompt = (
                    f"Write an in-depth article about '{topic}'. Include H1 title, meta description, "
                    f"table of contents, clear H2 sections with concrete examples, and a strong conclusion."
                )
                body = await self._call_gemini_api(prompt, system_prompt)
                lines = body.split("\n")
                title = lines[0].replace("#", "").strip() if lines else topic.title()
                return GenerateResponse(
                    topic=topic,
                    content_type=ContentType.BLOG,
                    tone=tone,
                    title=title,
                    body=body,
                    metadata={"read_time": "5 min", "word_count": str(len(body.split()))},
                )
            except Exception as e:
                logger.warning(f"Gemini API generation failed ({e}), falling back to offline engine.")

        return self._generate_offline(topic, tone, target_audience, keywords)

    def _generate_offline(
        self, topic: str, tone: Tone, target_audience: str, keywords: list
    ) -> GenerateResponse:
        title = f"The Definitive Guide to {topic.title()}"
        kw_tags = " ".join([f"`{k}`" for k in keywords]) if keywords else "`best-practices` `architecture`"

        markdown_body = f"""# {title}

> **Meta Description:** Discover how {topic} transforms workflows for {target_audience}. Actionable insights, architectural patterns, and practical execution.

---

## 📌 Executive Summary
In today's fast-evolving landscape, understanding **{topic}** has become a pivotal factor for success. Whether you are leading a team or building modern systems, mastering the core principles enables sustainable scaling and efficiency.

---

## 🎯 Key Pillars of Success
1. **Clear Foundation & Strategy**: Establish measurable benchmarks before rollout.
2. **Modular Execution**: Break complex workflows into composable, testable layers.
3. **Continuous Feedback**: Monitor latency, quality thresholds, and adoption metrics.

---

## 🛠️ Practical Implementation Blueprint
When integrating {topic} into your existing tech stack:
- **Phase 1: Discovery & Audit**: Identify baseline bottlenecks and resource boundaries.
- **Phase 2: Pilot Deployment**: Ship a minimum viable iteration with automated integration tests.
- **Phase 3: Scale & Automate**: Transition manual procedures into self-healing automated routines.

```python
# Reference configuration pattern for {topic}
config = {{
    "target": "{topic}",
    "mode": "optimized",
    "resilience": "fault-tolerant",
    "tags": [{", ".join(f'"{k}"' for k in keywords) if keywords else '"production"'}]
}}
```

---

## 💡 Key Takeaways
- Approaching **{topic}** with a rigorous framework eliminates technical and operational friction.
- Alignment across teams ensures consistent velocity and measurable ROI.
- Relevant topics: {kw_tags}

---

## 🚀 Call to Action
Ready to implement these patterns in your workflow? Share your thoughts and join the discussion below!
"""
        return GenerateResponse(
            topic=topic,
            content_type=ContentType.BLOG,
            tone=tone,
            title=title,
            body=markdown_body,
            metadata={
                "read_time": "4 min",
                "word_count": str(len(markdown_body.split())),
                "engine": "deterministic-offline",
            },
        )
