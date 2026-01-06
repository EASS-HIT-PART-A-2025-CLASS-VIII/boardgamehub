from typing import Optional
from sqlmodel import SQLModel, Field


class BoardGame(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    designer: Optional[str] = None
    year_published: Optional[int] = None

    min_players: int
    max_players: int

    play_time_min: Optional[int] = None  # minutes
    complexity: Optional[float] = None   # e.g. 1.0 - 5.0
    rating: Optional[float] = None       # e.g. 0.0 - 10.0
