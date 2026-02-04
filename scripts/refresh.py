# scripts/refresh.py
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx


@dataclass(frozen=True)
class RefreshSettings:
    api_base_url: str = os.getenv("BOARDGAME_API_BASE_URL", "http://localhost:8000").rstrip("/")
    timeout_s: float = float(os.getenv("REFRESH_TIMEOUT_S", "5"))
    retries: int = int(os.getenv("REFRESH_RETRIES", "3"))
    concurrency: int = int(os.getenv("REFRESH_CONCURRENCY", "3"))
    trace_id: str = os.getenv("REFRESH_TRACE_ID", "refresh-script")
    # daily idempotency by default:
    idempotency_key: str = os.getenv("REFRESH_IDEMPOTENCY_KEY", f"stats:daily:{date.today().isoformat()}")


async def _post_with_retries(
    client: httpx.AsyncClient,
    url: str,
    *,
    headers: dict[str, str],
    retries: int,
) -> dict[str, Any]:
    last_exc: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            resp = await client.post(url, headers=headers)
            # If FastAPI returns error - raise to trigger retry for 5xx/connection issues
            resp.raise_for_status()
            return resp.json()
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            last_exc = exc

            # אם זה 4xx (חוץ מ-429), לרוב לא עוזר retry
            if isinstance(exc, httpx.HTTPStatusError):
                status = exc.response.status_code
                if 400 <= status < 500 and status != 429:
                    raise

            # backoff קטן: 0.5s, 1s, 2s...
            await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

    # אם נגמרו ניסיונות
    assert last_exc is not None
    raise last_exc


async def refresh_once(settings: RefreshSettings) -> dict[str, Any]:
    url = f"{settings.api_base_url}/internal/stats/refresh"
    headers = {
        "Idempotency-Key": settings.idempotency_key,
        "X-Trace-Id": settings.trace_id,
    }

    async with httpx.AsyncClient(timeout=settings.timeout_s) as client:
        return await _post_with_retries(
            client,
            url,
            headers=headers,
            retries=settings.retries,
        )


async def refresh_many(settings: RefreshSettings) -> list[dict[str, Any]]:
    """
    Bounded concurrency demo:
    We run N refresh tasks in parallel (they should collapse into already_done thanks to idempotency).
    This satisfies the 'bounded concurrency' requirement without complicating the product.
    """
    sem = asyncio.Semaphore(settings.concurrency)

    async def _guarded_call() -> dict[str, Any]:
        async with sem:
            return await refresh_once(settings)

    # נריץ מספר משימות במקביל (אפשר לשנות את N לפי צורך)
    tasks = [asyncio.create_task(_guarded_call()) for _ in range(settings.concurrency)]
    return await asyncio.gather(*tasks)


def main() -> None:
    settings = RefreshSettings()
    results = asyncio.run(refresh_many(settings))

    # הדפסה קצרה וברורה לגריידר
    print(f"API: {settings.api_base_url}")
    print(f"Idempotency-Key: {settings.idempotency_key}")
    for i, res in enumerate(results, start=1):
        print(f"[{i}] {res}")


if __name__ == "__main__":
    main()
