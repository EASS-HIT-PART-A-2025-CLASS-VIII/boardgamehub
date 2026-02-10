from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel



class BoardGameBase(SQLModel):
    name: str
    designer: Optional[str] = None
    year_published: Optional[int] = None

    min_players: int
    max_players: int

    play_time_min: Optional[int] = None
    complexity: Optional[float] = None
    rating: Optional[float] = None


class BoardGameCreate(BoardGameBase):
    pass


class BoardGameRead(BoardGameBase):
    id: int


class BoardGameUpdate(SQLModel):
    name: Optional[str] = None
    designer: Optional[str] = None
    year_published: Optional[int] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    play_time_min: Optional[int] = None
    complexity: Optional[float] = None
    rating: Optional[float] = None

class TopRatedItem(SQLModel):
    id: int
    name: str
    rating: float


class StatsSnapshot(SQLModel):
    total_games: int
    avg_rating: Optional[float] = None
    avg_complexity: Optional[float] = None
    player_range_counts: dict[str, int] = {}
    top_rated: list[TopRatedItem] = []
    generated_at: datetime

