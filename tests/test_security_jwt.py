import uuid
import pytest
from jose import jwt
from httpx import AsyncClient
from app.config import Settings


@pytest.mark.anyio
async def test_refresh_requires_token(async_client: AsyncClient) -> None:
    r = await async_client.post("/internal/stats/refresh", headers={"Idempotency-Key": f"test:{uuid.uuid4().hex}"})
    assert r.status_code == 401


@pytest.mark.anyio
async def test_refresh_forbidden_for_wrong_role(async_client: AsyncClient) -> None:
    settings = Settings()
    bad_token = jwt.encode(
        {"sub": "x", "role": "user", "iss": settings.jwt_issuer, "aud": settings.jwt_audience},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    r = await async_client.post(
        "/internal/stats/refresh",
        headers={
            "Authorization": f"Bearer {bad_token}",
            "Idempotency-Key": f"test:{uuid.uuid4().hex}",
        },
    )
    assert r.status_code == 403


@pytest.mark.anyio
async def test_refresh_rejects_expired_token(async_client: AsyncClient) -> None:
    settings = Settings()
    # token expired in the past:
    expired = jwt.encode(
        {
            "sub": "admin",
            "role": "admin",
            "exp": 1,
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    r = await async_client.post(
        "/internal/stats/refresh",
        headers={
            "Authorization": f"Bearer {expired}",
            "Idempotency-Key": f"test:{uuid.uuid4().hex}",
        },
    )
    assert r.status_code == 401
