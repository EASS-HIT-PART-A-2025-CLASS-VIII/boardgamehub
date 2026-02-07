import asyncio
import os
import uuid
import httpx

API_BASE_URL = os.getenv("BOARDGAME_API_BASE_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("BOARDGAME_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("BOARDGAME_ADMIN_PASSWORD", "classroom")  
INTERVAL_SECONDS = int(os.getenv("BOARDGAME_WORKER_INTERVAL_SECONDS", "60"))

def build_idempotency_key() -> str:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return f"worker-stats-refresh:{now.strftime('%Y-%m-%d-%H')}"


async def fetch_token(client: httpx.AsyncClient) -> str:
    r = await client.post(
        "/auth/token",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    return data["access_token"]


async def refresh_stats_once(client: httpx.AsyncClient, token: str) -> dict:
    trace_id = str(uuid.uuid4())
    idem_key = build_idempotency_key()

    r = await client.post(
        "/internal/stats/refresh",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": idem_key,
            "X-Trace-Id": trace_id,
        },
        timeout=30,
    )
    # 401/403 → נרצה לנסות להביא token מחדש בלולאה
    if r.status_code in (401, 403):
        return {"status": "auth_error", "code": r.status_code, "body": r.text, "trace_id": trace_id}

    r.raise_for_status()
    return {"status": "ok", "trace_id": trace_id, "idempotency_key": idem_key, "response": r.json()}


async def main():
    print(f"[worker] starting. api={API_BASE_URL} interval={INTERVAL_SECONDS}s")
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        token = None

        while True:
            try:
                # Ensure token
                if not token:
                    token = await fetch_token(client)
                    print("[worker] obtained token")

                result = await refresh_stats_once(client, token)

                if result["status"] == "auth_error":
                    print(f"[worker] auth error {result['code']} trace={result['trace_id']} -> re-login")
                    token = None
                else:
                    # response expected: {status: updated/already_done, ...}
                    resp = result["response"]
                    print(
                        f"[worker] refresh ok status={resp.get('status')} "
                        f"idem={result['idempotency_key']} trace={result['trace_id']}"
                    )

            except httpx.HTTPError as e:
                print(f"[worker] http error: {e}")
            except Exception as e:
                print(f"[worker] unexpected error: {e}")

            await asyncio.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
