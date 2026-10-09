"""Social Media Content Generator for X/Twitter, LinkedIn, Instagram, and Telegram."""

import logging
from content_studio.config import Settings
from content_studio.models.content import ContentType, Tone
from content_studio.models.generation import GenerateResponse
from content_studio.engine.base import BaseGenerator

logger = logging.getLogger(__name__)


class SocialGenerator(BaseGenerator):
    """Generates channel-tailored social media copy."""

    async def generate(
        self,
        topic: str,
        content_type: ContentType,
        tone: Tone = Tone.CONVERSATIONAL,
        keywords: list = None,
    ) -> GenerateResponse:
        keywords = keywords or []
        kw_str = ", ".join(keywords) if keywords else "tech, innovation"

        if self.settings.gemini_api_key:
            try:
                system_prompt = (
                    f"You are an elite social media growth strategist.\n"
                    f"Generate a high-converting, platform-optimized post for {content_type.value.upper()}.\n"
                    f"Tone: {tone.value}. Keywords: {kw_str}."
                )
                prompt = (
                    f"Craft a compelling {content_type.value} post about '{topic}'. "
                    f"Follow exact channel conventions: punchy hook, clean line breaks, high retention, and strong CTA."
                )
                body = await self._call_gemini_api(prompt, system_prompt)
                title = f"{content_type.value.upper()}: {topic[:50]}"
                return GenerateResponse(
                    topic=topic,
                    content_type=content_type,
                    tone=tone,
                    title=title,
                    body=body,
                    metadata={"channel": content_type.value, "char_count": str(len(body))},
                )
            except Exception as e:
                logger.warning(f"Social generation failed with Gemini ({e}), falling back to offline.")

        return self._generate_offline(topic, content_type, tone, keywords)

    def _generate_offline(
        self, topic: str, content_type: ContentType, tone: Tone, keywords: list
    ) -> GenerateResponse:
        hashtags = " ".join([f"#{k.replace(' ', '')}" for k in keywords]) if keywords else f"#{topic.replace(' ', '')} #Innovation #Tech"

        if content_type == ContentType.TWEET:
            title = f"X Thread: {topic.title()}"
            body = (
                f"🧵 1/4 Most people approach {topic} completely wrong.\n\n"
                f"Here is the exact playbook to master it in 2026 (without wasting weeks):\n\n"
                f"---\n"
                f"2/4 1️⃣ Focus on Fundamentals first.\n"
                f"Shiny tools come and go, but robust fundamentals compound forever.\n\n"
                f"---\n"
                f"3/4 2️⃣ Automate the repetitive bottlenecks.\n"
                f"Every hour saved on manual toil is an hour reinvested in leverage.\n\n"
                f"---\n"
                f"4/4 Bookmark this thread 🔖 if you found it valuable.\n\n"
                f"What is your biggest hurdle with {topic}? Drop it below 👇\n\n"
                f"{hashtags}"
            )
        elif content_type == ContentType.LINKEDIN:
            title = f"LinkedIn Post: {topic.title()}"
            body = (
                f"Most leaders talk about {topic}.\n"
                f"Very few actually execute it with engineering discipline.\n\n"
                f"Here is what 5 years of scaling taught our team:\n\n"
                f"👉 Complexity is the enemy of execution.\n"
                f"👉 Clear architecture beats brilliant improvisation.\n"
                f"👉 Automated testing and observability build unstoppable momentum.\n\n"
                f"If you are prioritizing {topic} this quarter, start with a solid foundation before adding layers of complexity.\n\n"
                f"Agree or disagree? How is your team approaching this?\n\n"
                f"{hashtags}"
            )
        elif content_type == ContentType.INSTAGRAM:
            title = f"Instagram Post: {topic.title()}"
            body = (
                f"✨ The Blueprint for {topic.title()} ✨\n\n"
                f"Swipe to see how top teams build and scale without burning out 📲\n\n"
                f"💡 3 Key Steps:\n"
                f"1. Audit your current bottlenecks\n"
                f"2. Implement modular workflows\n"
                f"3. Measure real-world outcomes\n\n"
                f"Save this post for your next planning session! 📌\n\n"
                f".\n.\n.\n"
                f"{hashtags}"
            )
        elif content_type == ContentType.TELEGRAM:
            title = f"Telegram Post: {topic.title()}"
            body = (
                f"🔥 **{topic.title()} — Amaliy Qo'llanma**\n\n"
                f"Bugungi kunda **{topic}** sohasida eng muhim bo'lgan 3 ta asosiy qoida:\n\n"
                f"• **1. Aniq arxitektura**: Loyihani toza va modulli strukturada quring.\n"
                f"• **2. Avtomatlashtirish**: Qaytariluvchi ishlarni skriptlar orqali tejang.\n"
                f"• **3. Sifat nazorati**: Har doim testlar bilan mustahkamlang.\n\n"
                f"💬 _Fikringizni izohlarda qoldiring!_\n\n"
                f"{hashtags}"
            )
        else:
            title = f"Social Post: {topic.title()}"
            body = f"Key thoughts on {topic}: execution beats intention every time. {hashtags}"

        return GenerateResponse(
            topic=topic,
            content_type=content_type,
            tone=tone,
            title=title,
            body=body,
            metadata={"channel": content_type.value, "char_count": str(len(body)), "engine": "deterministic-offline"},
        )
