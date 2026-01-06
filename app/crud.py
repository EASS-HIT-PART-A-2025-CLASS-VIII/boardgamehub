from sqlmodel import Session, select
from sqlalchemy import func

from app.models import BoardGame


def list_boardgames(session: Session) -> list[BoardGame]:
    return session.exec(select(BoardGame)).all()


def get_boardgame(session: Session, boardgame_id: int) -> BoardGame | None:
    return session.get(BoardGame, boardgame_id)


def get_boardgame_by_name(session: Session, name: str) -> BoardGame | None:
    if not name:
        return None
    return session.exec(
        select(BoardGame).where(func.lower(BoardGame.name) == name.strip().lower())
    ).first()


def create_boardgame(session: Session, boardgame: BoardGame) -> BoardGame:
    existing = get_boardgame_by_name(session, boardgame.name)
    if existing:
        raise ValueError("Board game with this name already exists")

    session.add(boardgame)
    session.commit()
    session.refresh(boardgame)
    return boardgame


def update_boardgame(session: Session, boardgame_id: int, data: dict) -> BoardGame | None:
    db_obj = get_boardgame(session, boardgame_id)
    if not db_obj:
        return None

    # אם משנים שם - לוודא שאין כפילות (מלבד עצמו)
    new_name = data.get("name")
    if new_name is not None:
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Name cannot be empty")

        if new_name.lower() != db_obj.name.lower():
            existing = get_boardgame_by_name(session, new_name)
            if existing:
                raise ValueError("Board game with this name already exists")

        data["name"] = new_name

    for k, v in data.items():
        setattr(db_obj, k, v)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def delete_boardgame(session: Session, boardgame_id: int) -> bool:
    db_obj = get_boardgame(session, boardgame_id)
    if not db_obj:
        return False
    session.delete(db_obj)
    session.commit()
    return True
