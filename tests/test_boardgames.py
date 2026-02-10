import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.database import get_session
from app.models import BoardGame  # noqa: F401


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",  
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )

    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers():
    from datetime import timedelta
    from app.config import Settings
    from app.security import create_access_token
    settings = Settings()
    token = create_access_token(
        subject=settings.admin_username,
        role="admin",
        settings=settings,
        expires_delta=timedelta(minutes=1),
    )
    return {"Authorization": f"Bearer {token}"}



def test_create_boardgame(client: TestClient, auth_headers: dict):
    payload = {
        "name": "Catan",
        "designer": "Klaus Teuber",
        "year_published": 1995,
        "min_players": 3,
        "max_players": 4,
        "play_time_min": 60,
        "complexity": 2.3,
        "rating": 7.2,
    }

    res = client.post("/boardgames/", json=payload, headers=auth_headers)
    assert res.status_code == 201

    data = res.json()
    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["min_players"] == payload["min_players"]


def test_list_boardgames(client: TestClient, auth_headers: dict):
    client.post("/boardgames/", json={"name": "Catan", "min_players": 3, "max_players": 4}, headers=auth_headers)
    client.post("/boardgames/", json={"name": "7 Wonders", "min_players": 2, "max_players": 7}, headers=auth_headers)

    res = client.get("/boardgames/")
    assert res.status_code == 200

    data = res.json()
    items = data["items"]
    assert isinstance(items, list)
    assert len(items) == 2
    assert {x["name"] for x in items} == {"Catan", "7 Wonders"}


def test_get_boardgame_by_id(client: TestClient, auth_headers: dict):
    create = client.post(
        "/boardgames/",
        json={"name": "Terraforming Mars", "min_players": 1, "max_players": 5},
        headers=auth_headers,
    )
    bg_id = create.json()["id"]

    res = client.get(f"/boardgames/{bg_id}")
    assert res.status_code == 200

    data = res.json()
    assert data["id"] == bg_id
    assert data["name"] == "Terraforming Mars"


def test_update_boardgame(client: TestClient, auth_headers: dict):
    create = client.post(
        "/boardgames/",
        json={"name": "Catan", "min_players": 3, "max_players": 4, "rating": 7.2},
        headers=auth_headers,
    )
    bg_id = create.json()["id"]

    update_payload = {
        "name": "Catan (Updated)",
        "min_players": 3,
        "max_players": 4,
        "rating": 8.0,
    }

    res = client.put(f"/boardgames/{bg_id}", json=update_payload, headers=auth_headers)
    assert res.status_code == 200

    data = res.json()
    assert data["id"] == bg_id
    assert data["name"] == "Catan (Updated)"
    assert data["rating"] == 8.0


def test_delete_boardgame(client: TestClient, auth_headers: dict):
    create = client.post(
        "/boardgames/",
        json={"name": "Splendor", "min_players": 2, "max_players": 4},
        headers=auth_headers,
    )
    bg_id = create.json()["id"]

    res = client.delete(f"/boardgames/{bg_id}", headers=auth_headers)
    assert res.status_code == 204

    res2 = client.get(f"/boardgames/{bg_id}")
    assert res2.status_code == 404


def test_get_nonexistent_returns_404(client: TestClient):
    res = client.get("/boardgames/999999")
    assert res.status_code == 404
