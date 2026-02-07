from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.config import Settings
from app.security import create_access_token, get_settings, verify_password


router = APIRouter(prefix="/auth", tags=["Auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token", response_model=TokenResponse)
def token(payload: LoginRequest, settings: Settings = Depends(get_settings)) -> TokenResponse:
    if payload.username != settings.admin_username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")

    if not verify_password(payload.password, settings.admin_password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")

    token = create_access_token(
        subject=payload.username,
        role="admin",
        settings=settings,
        expires_delta=timedelta(minutes=settings.jwt_access_token_minutes),
    )
    return TokenResponse(access_token=token)