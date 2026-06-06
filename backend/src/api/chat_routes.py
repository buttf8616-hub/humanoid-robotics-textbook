"""Simple Groq-powered chat endpoint (no RAG retrieval required)."""
import time
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from src.config import settings

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_PROMPT = """You are an expert AI assistant for the Physical AI & Humanoid Robotics textbook.
Answer questions about robotics, physical AI, humanoid robots, sensors, actuators, control systems,
machine learning for robotics, and related topics. Be concise, accurate, and educational.
If a question is unrelated to robotics or AI, gently redirect to the textbook topics."""


class ConversationMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    selected_context: Optional[dict] = None
    conversation_history: Optional[list[ConversationMessage]] = None


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    answer: str
    sources: list = []
    confidence: str = "medium"
    latency_ms: float = 0.0
    tokens_used: TokenUsage = TokenUsage()


@chat_router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty")

    if not settings.groq_api_key:
        raise HTTPException(status_code=503, detail="Chat service not configured")

    client = AsyncOpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if request.conversation_history:
        for msg in request.conversation_history[-6:]:
            messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": request.question})

    start = time.time()
    try:
        resp = await client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens,
        )
        latency_ms = (time.time() - start) * 1000
        answer = resp.choices[0].message.content or ""
        usage = resp.usage

        return ChatResponse(
            answer=answer,
            sources=[],
            confidence="high" if len(answer) > 100 else "medium",
            latency_ms=round(latency_ms, 2),
            tokens_used=TokenUsage(
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
            ),
        )
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=503, detail="Chat service temporarily unavailable")
