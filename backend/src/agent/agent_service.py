"""Agent service for orchestrating LLM-based question answering."""
import asyncio
import json
import logging
import time
from typing import Optional

from openai import AsyncOpenAI, RateLimitError, APITimeoutError

from src.config import settings
from src.agent.prompts import get_system_prompt
from src.agent.tools import retrieve_book_content, RETRIEVE_BOOK_CONTENT_SCHEMA

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing AI agent interactions with retrieval-augmented answering."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )
        self.model = settings.groq_model
        self.temperature = settings.groq_temperature
        self.max_tokens = settings.groq_max_tokens
        self.timeout = settings.agent_timeout_seconds
        self.system_prompt = get_system_prompt()
        self.tools = [RETRIEVE_BOOK_CONTENT_SCHEMA]
        logger.info(f"AgentService initialised — model={self.model}")

    async def answer(
        self,
        question: str,
        top_k: int = 10,
        url_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        conversation_history: Optional[list[dict]] = None,
    ) -> dict:
        start = time.perf_counter()
        logger.info(f"Agent query: '{question[:100]}'")

        messages = [{"role": "system", "content": self.system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": question})

        try:
            # Turn 1: agent calls retrieval tool
            resp1 = await self._call_with_retry(
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
            )

            assistant_msg = resp1.choices[0].message
            tool_calls = assistant_msg.tool_calls

            if not tool_calls:
                logger.warning("Agent did not call retrieval tool")
                return {
                    "answer": "I need to retrieve information from the textbook to answer your question. Please try again.",
                    "sources": [],
                    "confidence": "refused",
                    "latency_ms": (time.perf_counter() - start) * 1000,
                    "tokens_used": {"prompt": resp1.usage.prompt_tokens,
                                    "completion": resp1.usage.completion_tokens,
                                    "total": resp1.usage.total_tokens},
                }

            # Execute tool calls
            tool_results = []
            all_sources: list[dict] = []

            for tc in tool_calls:
                if tc.function.name == "retrieve_book_content":
                    args = json.loads(tc.function.arguments)
                    result = await retrieve_book_content(
                        query=args.get("query", question),
                        top_k=args.get("top_k", top_k),
                        url_filter=args.get("url_filter", url_filter),
                        section_filter=args.get("section_filter", section_filter),
                    )
                    tool_results.append({
                        "tool_call_id": tc.id,
                        "role": "tool",
                        "name": tc.function.name,
                        "content": json.dumps(result),
                    })
                    for chunk in result.get("results", []):
                        all_sources.append({
                            "url": chunk.get("url", ""),
                            "title": chunk.get("title", ""),
                            "section": chunk.get("section", ""),
                            "chunk_index": chunk.get("chunk_index", 0),
                            "score": chunk.get("score", 0.0),
                            "excerpt": chunk.get("content", "")[:200],
                        })

            # Append assistant + tool result turns
            messages.append({
                "role": "assistant",
                "content": assistant_msg.content,
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in tool_calls
                ],
            })
            messages.extend(tool_results)

            # Turn 2: generate final answer
            resp2 = await self._call_with_retry(messages=messages)
            answer_text = resp2.choices[0].message.content

            # Apply filters
            if url_filter or section_filter:
                all_sources = [
                    s for s in all_sources
                    if (not url_filter or s["url"] == url_filter)
                    and (not section_filter or section_filter.lower() in s["section"].lower())
                ]

            confidence = self._detect_confidence(answer_text, all_sources)
            latency_ms = (time.perf_counter() - start) * 1000
            total_tokens = {
                "prompt": resp1.usage.prompt_tokens + resp2.usage.prompt_tokens,
                "completion": resp1.usage.completion_tokens + resp2.usage.completion_tokens,
                "total": resp1.usage.total_tokens + resp2.usage.total_tokens,
            }

            logger.info(f"Agent done — sources={len(all_sources)}, confidence={confidence}, latency={latency_ms:.0f}ms")
            return {"answer": answer_text, "sources": all_sources,
                    "confidence": confidence, "latency_ms": latency_ms,
                    "tokens_used": total_tokens}

        except Exception as exc:
            logger.error(f"Agent error: {exc}")
            raise

    async def _call_with_retry(self, messages, tools=None, tool_choice=None, max_retries=3):
        for attempt in range(max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "timeout": self.timeout,
                }
                if tools:
                    kwargs["tools"] = tools
                if tool_choice:
                    kwargs["tool_choice"] = tool_choice
                return await self.client.chat.completions.create(**kwargs)
            except RateLimitError:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"Rate limit, retrying in {wait}s ({attempt+1}/{max_retries})")
                    await asyncio.sleep(wait)
                else:
                    logger.error("Rate limit exceeded after retries")
                    raise
            except APITimeoutError:
                if attempt < max_retries - 1:
                    logger.warning(f"Timeout, retrying ({attempt+1}/{max_retries})")
                    await asyncio.sleep(1)
                else:
                    raise

    def _detect_confidence(self, answer: str, sources: list[dict]) -> str:
        answer_lower = answer.lower()
        if any(p in answer_lower for p in
               ["i don't have information", "i don't know",
                "not in the textbook", "no information about"]):
            return "refused"
        if not sources:
            return "refused"
        avg_score = sum(s["score"] for s in sources) / len(sources)
        if avg_score >= 0.8 and len(sources) >= 3:
            return "high"
        elif avg_score >= 0.6 and len(sources) >= 2:
            return "medium"
        return "low"
