import os
import uuid
from datetime import timedelta

import httpx
import pytest
from jose import jwt

from app.config import Settings


API_BASE_URL = os.getenv("BOARDGAME_API_BASE_URL", "http://localhost:8000").rstrip("/")


@pytest.mark.anyio
async def test_refresh_requires_token() -> None:
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=5.0) as client:
        r = await client.post("/internal/stats/refresh", headers={"Idempotency-Key": f"test:{uuid.uuid4().hex}"})
        assert r.status_code == 401


@pytest.mark.anyio
async def test_refresh_forbidden_for_wrong_role() -> None:
    settings = Settings()
    bad_token = jwt.encode({"sub": "x", "role": "user"}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=5.0) as client:
        r = await client.post(
            "/internal/stats/refresh",
            headers={
                "Authorization": f"Bearer {bad_token}",
                "Idempotency-Key": f"test:{uuid.uuid4().hex}",
            },
        )
        assert r.status_code == 403


@pytest.mark.anyio
async def test_refresh_rejects_expired_token() -> None:
    settings = Settings()
    # token expired in the past:
    expired = jwt.encode({"sub": "admin", "role": "admin", "exp": 1}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=5.0) as client:
        r = await client.post(
            "/internal/stats/refresh",
            headers={
                "Authorization": f"Bearer {expired}",
                "Idempotency-Key": f"test:{uuid.uuid4().hex}",
            },
        )
        assert r.status_code == 401
