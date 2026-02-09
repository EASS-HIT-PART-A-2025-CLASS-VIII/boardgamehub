import uuid
import pytest
from httpx import AsyncClient
from jose import jwt
from app.config import Settings

@pytest.mark.anyio
async def test_refresh_is_idempotent_and_stats_available(async_client: AsyncClient) -> None:
    idem_key = f"test:stats:{uuid.uuid4().hex}"
    
    # Generate Admin Token
    settings = Settings()
    token = jwt.encode(
        {"sub": "admin", "role": "admin", "iss": settings.jwt_issuer, "aud": settings.jwt_audience},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    headers = {
        "Idempotency-Key": idem_key, 
        "X-Trace-Id": "pytest-refresh",
        "Authorization": f"Bearer {token}"
    }

    # 1) First refresh should "update"
    r1 = await async_client.post(
        "/internal/stats/refresh",
        headers=headers,
    )
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["status"] in {"updated", "already_done"}
    assert body1["idempotency_key"] == idem_key

    # 2) Second refresh with same key must be "already_done"
    r2 = await async_client.post(
        "/internal/stats/refresh",
        headers=headers,
    )
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["status"] == "already_done"
    assert body2["idempotency_key"] == idem_key

    # 3) Stats endpoint should now return a snapshot
    r3 = await async_client.get("/stats")
    assert r3.status_code == 200
    stats = r3.json()

    assert "total_games" in stats
    assert isinstance(stats["total_games"], int)
    assert "generated_at" in stats
    assert "player_range_counts" in stats
