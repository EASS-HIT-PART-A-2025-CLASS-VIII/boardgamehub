from typing import NoReturn
import os
import httpx

BASE_URL = os.getenv("BOARDGAME_API_BASE_URL", "http://127.0.0.1:8000")
_client = httpx.Client(base_url=BASE_URL, timeout=600.0)


def set_auth_token(token: str | None) -> None:
    if token:
        _client.headers["Authorization"] = f"Bearer {token}"
    else:
        if "Authorization" in _client.headers:
            del _client.headers["Authorization"]


def login(username: str, password: str) -> str:
    try:
        r = _client.post("/auth/token", data={"username": username, "password": password})
        r.raise_for_status()
        token = r.json()["access_token"]
        set_auth_token(token)
        return token
    except httpx.HTTPStatusError as e:
        _raise_clean_error(e)
    except httpx.RequestError as e:
        _raise_request_error(e)


def _raise_clean_error(e: httpx.HTTPStatusError) -> NoReturn:
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


def _raise_request_error(e: httpx.RequestError) -> NoReturn:
    raise RuntimeError(f"Cannot reach API at {BASE_URL}. Error: {e}")


def list_boardgames(
    page: int = 1, 
    page_size: int = 10,
    search: str | None = None,
    min_players: int | None = None,
    max_players: int | None = None,
) -> dict:
    params = {"page": page, "page_size": page_size}
    if search:
        params["search"] = search
    if min_players is not None:
        params["min_players"] = min_players
    if max_players is not None:
        params["max_players"] = max_players

    try:
        r = _client.get("/boardgames/", params=params)
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


def upload_csv(file_content: bytes, filename: str) -> dict:
    files = {"file": (filename, file_content, "text/csv")}
    try:
        r = _client.post("/boardgames/upload", files=files)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _raise_clean_error(e)
    except httpx.RequestError as e:
        _raise_request_error(e)
