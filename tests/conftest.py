import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session
from app.redis_client import get_redis_client

class MockRedis:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value):
        self.data[key] = value
        return True

    async def setex(self, key, time, value):
        self.data[key] = value
        return True

    async def exists(self, key):
        return 1 if key in self.data else 0

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def mock_redis():
    return MockRedis()

@pytest.fixture
async def async_client(session, mock_redis) -> AsyncGenerator[AsyncClient, None]:
    def get_session_override():
        yield session

    def get_redis_override():
        return mock_redis

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_redis_client] = get_redis_override

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
