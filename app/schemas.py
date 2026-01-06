from typing import Optional
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
