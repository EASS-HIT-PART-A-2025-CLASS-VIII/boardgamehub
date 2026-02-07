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

    # --- JWT login settings (KISS) ---
    token_path: str = os.getenv("REFRESH_TOKEN_PATH", "/auth/token")
    admin_username: str = os.getenv("BOARDGAME_ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("BOARDGAME_ADMIN_PASSWORD", "classroom")


async def _post_with_retries(
    client: httpx.AsyncClient,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json: dict[str, Any] | None = None,
    retries: int,
) -> dict[str, Any]:
    last_exc: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            resp = await client.post(url, headers=headers, json=json)

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


async def _get_token(client: httpx.AsyncClient, settings: RefreshSettings) -> str:
    """
    KISS: login once, reuse token for the whole refresh run.
    Assumes /auth/token accepts JSON: {"username": "...", "password": "..."}
    """
    data = await _post_with_retries(
        client,
        settings.token_path,
        json={"username": settings.admin_username, "password": settings.admin_password},
        retries=settings.retries,
    )
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"Token endpoint did not return access_token. Response: {data}")
    return token


async def refresh_once(
    client: httpx.AsyncClient,
    settings: RefreshSettings,
    *,
    token: str,
) -> dict[str, Any]:
    url = "/internal/stats/refresh"
    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": settings.idempotency_key,
        "X-Trace-Id": settings.trace_id,
    }

    return await _post_with_retries(
        client,
        url,
        headers=headers,
        retries=settings.retries,
    )


async def refresh_many(settings: RefreshSettings) -> list[dict[str, Any]]:
    sem = asyncio.Semaphore(settings.concurrency)

    async with httpx.AsyncClient(base_url=settings.api_base_url, timeout=settings.timeout_s) as client:
        token = await _get_token(client, settings)

        async def _guarded_call() -> dict[str, Any]:
            async with sem:
                return await refresh_once(client, settings, token=token)

        tasks = [asyncio.create_task(_guarded_call()) for _ in range(settings.concurrency)]
        return await asyncio.gather(*tasks)


def main() -> None:
    settings = RefreshSettings()
    results = asyncio.run(refresh_many(settings))

    # הדפסה קצרה וברורה לגריידר
    print(f"API: {settings.api_base_url}")
    print(f"Token endpoint: {settings.token_path}")
    print(f"Idempotency-Key: {settings.idempotency_key}")
    for i, res in enumerate(results, start=1):
        print(f"[{i}] {res}")


if __name__ == "__main__":
    main()
