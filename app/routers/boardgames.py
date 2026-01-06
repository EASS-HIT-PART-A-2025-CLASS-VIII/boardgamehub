from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app import crud
from app.models import BoardGame
from app.schemas import BoardGameCreate, BoardGameRead, BoardGameUpdate

router = APIRouter(prefix="/boardgames", tags=["BoardGames"])


@router.get("/", response_model=list[BoardGameRead])
def list_boardgames(session: Session = Depends(get_session)):
    return crud.list_boardgames(session)


@router.post("/", response_model=BoardGameRead, status_code=201)
def create_boardgame(payload: BoardGameCreate, session: Session = Depends(get_session)):
    boardgame_obj = BoardGame(**payload.model_dump())
    try:
        return crud.create_boardgame(session, boardgame_obj)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{boardgame_id}", response_model=BoardGameRead)
def get_boardgame(boardgame_id: int, session: Session = Depends(get_session)):
    game = crud.get_boardgame(session, boardgame_id)
    if not game:
        raise HTTPException(status_code=404, detail="Board game not found")
    return game


@router.put("/{boardgame_id}", response_model=BoardGameRead)
def update_boardgame(
    boardgame_id: int,
    payload: BoardGameUpdate,
    session: Session = Depends(get_session),
):
    try:
        updated = crud.update_boardgame(
            session,
            boardgame_id,
            payload.model_dump(exclude_unset=True),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not updated:
        raise HTTPException(status_code=404, detail="Board game not found")
    return updated


@router.delete("/{boardgame_id}", status_code=204)
def delete_boardgame(boardgame_id: int, session: Session = Depends(get_session)):
    ok = crud.delete_boardgame(session, boardgame_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Board game not found")
    return None
