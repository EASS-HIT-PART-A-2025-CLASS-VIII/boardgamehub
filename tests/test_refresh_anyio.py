import os
import uuid

import httpx
import pytest


API_BASE_URL = os.getenv("BOARDGAME_API_BASE_URL", "http://localhost:8000").rstrip("/")


@pytest.mark.anyio
async def test_refresh_is_idempotent_and_stats_available() -> None:
    idem_key = f"test:stats:{uuid.uuid4().hex}"

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=5.0) as client:
        # 1) First refresh should "update"
        r1 = await client.post(
            "/internal/stats/refresh",
            headers={"Idempotency-Key": idem_key, "X-Trace-Id": "pytest-refresh"},
        )
        r1.raise_for_status()
        body1 = r1.json()
        assert body1["status"] in {"updated", "already_done"}
        assert body1["idempotency_key"] == idem_key

        # 2) Second refresh with same key must be "already_done"
        r2 = await client.post(
            "/internal/stats/refresh",
            headers={"Idempotency-Key": idem_key, "X-Trace-Id": "pytest-refresh"},
        )
        r2.raise_for_status()
        body2 = r2.json()
        assert body2["status"] == "already_done"
        assert body2["idempotency_key"] == idem_key

        # 3) Stats endpoint should now return a snapshot
        r3 = await client.get("/stats")
        r3.raise_for_status()
        stats = r3.json()

        assert "total_games" in stats
        assert isinstance(stats["total_games"], int)
        assert "generated_at" in stats
        assert "player_range_counts" in stats
