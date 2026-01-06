from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.config import settings

from pathlib import Path

if settings.database_url.startswith("sqlite:///"):
    Path("data").mkdir(exist_ok=True)

DATABASE_URL = settings.database_url

engine_kwargs = {
    "echo": settings.database_echo,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

if DATABASE_URL == "sqlite://":
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **engine_kwargs)


def create_db_and_tables() -> None:
    import app.models  # noqa: F401  # register SQLModel models in metadata
    SQLModel.metadata.create_all(engine)



def get_session():
    with Session(engine) as session:
        yield session
