import os
import httpx

BASE_URL = os.getenv("BOARDGAME_API_BASE_URL", "http://127.0.0.1:8000")
_client = httpx.Client(base_url=BASE_URL, timeout=10.0)


def _raise_clean_error(e: httpx.HTTPStatusError) -> None:
    """
    Convert FastAPI error responses into a clean Python exception message.
    Expected FastAPI format: {"detail": "..."}.
    """
    try:
        data = e.response.json()
        detail = data.get("detail")
    except Exception:
        detail = None

    if detail:
        raise RuntimeError(detail)

    raise RuntimeError(f"Request failed with status {e.response.status_code}")


def _raise_request_error(e: httpx.RequestError) -> None:
    raise RuntimeError(f"Cannot reach API at {BASE_URL}. Error: {e}")


def list_boardgames() -> list[dict]:
    try:
        r = _client.get("/boardgames/")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _raise_clean_error(e)
    except httpx.RequestError as e:
        _raise_request_error(e)


def create_boardgame(payload: dict) -> dict:
    try:
        r = _client.post("/boardgames/", json=payload)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _raise_clean_error(e)
    except httpx.RequestError as e:
        _raise_request_error(e)


def update_boardgame(boardgame_id: int, payload: dict) -> dict:
    try:
        r = _client.put(f"/boardgames/{boardgame_id}", json=payload)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _raise_clean_error(e)
    except httpx.RequestError as e:
        _raise_request_error(e)


def delete_boardgame(boardgame_id: int) -> None:
    try:
        r = _client.delete(f"/boardgames/{boardgame_id}")
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        _raise_clean_error(e)
    except httpx.RequestError as e:
        _raise_request_error(e)
