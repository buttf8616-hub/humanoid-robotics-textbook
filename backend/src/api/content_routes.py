"""Content personalization and translation API routes."""
import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from src.services.auth_service import get_user_by_id, verify_token
from src.services.content_service import ContentService

logger = logging.getLogger(__name__)

content_router = APIRouter(prefix="/content", tags=["content"])


def _get_user(authorization: Optional[str]) -> dict:
    """Extract and validate user from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    payload = verify_token(authorization.split(" ", 1)[1])
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_user_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class PersonalizeRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Chapter text content from the page")
    chapter_title: str = Field(default="", description="Chapter title for context")


class TranslateRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Chapter text content from the page")
    chapter_title: str = Field(default="", description="Chapter title for context")


class ContentResponse(BaseModel):
    result: str
    user_name: str = ""


@content_router.post("/personalize", response_model=ContentResponse)
async def personalize(
    request: PersonalizeRequest,
    authorization: Optional[str] = Header(None),
) -> ContentResponse:
    """Personalize chapter content based on the logged-in student's background."""
    user = _get_user(authorization)
    service = ContentService()
    try:
        result = await service.personalize(
            content=request.content,
            software_background=user.get("software_background", ""),
            hardware_background=user.get("hardware_background", ""),
            user_name=user.get("name", ""),
        )
        return ContentResponse(result=result, user_name=user.get("name", ""))
    except Exception as e:
        logger.error(f"Personalization failed: {e}")
        raise HTTPException(status_code=503, detail="Personalization service temporarily unavailable")


@content_router.post("/translate", response_model=ContentResponse)
async def translate(
    request: TranslateRequest,
    authorization: Optional[str] = Header(None),
) -> ContentResponse:
    """Translate chapter content to Urdu."""
    user = _get_user(authorization)
    service = ContentService()
    try:
        result = await service.translate_to_urdu(content=request.content)
        return ContentResponse(result=result, user_name=user.get("name", ""))
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=503, detail="Translation service temporarily unavailable")
