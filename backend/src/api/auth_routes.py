"""Authentication API routes: signup, signin, me."""
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from src.services.auth_service import (
    authenticate_user,
    create_token,
    create_user,
    get_user_by_id,
    verify_token,
)

from .auth_schemas import AuthResponse, SigninRequest, SignupRequest, UserInfo

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def _user_info(user: dict) -> UserInfo:
    return UserInfo(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        code_id=user["code_id"],
        software_background=user.get("software_background", ""),
        hardware_background=user.get("hardware_background", ""),
    )


@auth_router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest) -> AuthResponse:
    """Register a new student account with PIAIC code and background profile."""
    try:
        user = create_user(
            request.email,
            request.name,
            request.code_id,
            request.password,
            request.software_background,
            request.hardware_background,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return AuthResponse(token=create_token(user["id"], user["email"]), user=_user_info(user))


@auth_router.post("/signin", response_model=AuthResponse)
async def signin(request: SigninRequest) -> AuthResponse:
    """Sign in with email and password."""
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthResponse(token=create_token(user["id"], user["email"]), user=_user_info(user))


@auth_router.get("/me", response_model=UserInfo)
async def me(authorization: Optional[str] = Header(None)) -> UserInfo:
    """Get current user info from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_user_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_info(user)
