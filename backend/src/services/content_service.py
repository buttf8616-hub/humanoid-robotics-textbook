"""AI content service: personalization and Urdu translation using Groq."""
from openai import AsyncOpenAI

from src.config import settings

_MAX_CONTENT = 6000  # chars — stay within Groq context limits


class ContentService:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )

    async def personalize(
        self,
        content: str,
        software_background: str,
        hardware_background: str,
        user_name: str = "",
    ) -> str:
        """Return a version of content adapted to the student's background."""
        name_line = f"Student name: {user_name}\n" if user_name else ""
        system = f"""You are a personalized AI tutor for a Physical AI & Humanoid Robotics textbook.

{name_line}Student background profile:
- Software / Programming level: {software_background or "not specified"}
- Hardware / Electronics level: {hardware_background or "not specified"}

Your job: rewrite the chapter content so it perfectly matches this student's background.
Guidelines:
- Beginner software: avoid code snippets, use plain analogies, define every acronym.
- Advanced software: include code examples, reference industry tools, skip basics.
- No hardware background: explain every circuit/sensor term from scratch.
- Advanced hardware: use technical specs, skip introductory explanations.
- Always keep all factual content intact — only change the presentation style.
- Use clear markdown headings (##) and bullet points.
- Open with one sentence greeting the student by name (if provided)."""

        resp = await self._client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"Personalize this chapter content for me:\n\n{content[:_MAX_CONTENT]}",
                },
            ],
            temperature=0.4,
            max_tokens=3000,
        )
        return resp.choices[0].message.content

    async def translate_to_urdu(self, content: str) -> str:
        """Translate chapter content to Urdu, preserving structure."""
        resp = await self._client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert translator specializing in technical and scientific texts. "
                        "Translate the following robotics textbook chapter to Urdu. "
                        "Rules:\n"
                        "- Preserve all markdown headings (##, ###) and bullet points.\n"
                        "- Keep technical terms in English with Urdu explanation in parentheses.\n"
                        "- Keep code blocks, URLs, and proper nouns in English.\n"
                        "- Write Urdu in Nastaliq script (not Roman Urdu)."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Translate this chapter to Urdu:\n\n{content[:_MAX_CONTENT]}",
                },
            ],
            temperature=0.1,
            max_tokens=4000,
        )
        return resp.choices[0].message.content
