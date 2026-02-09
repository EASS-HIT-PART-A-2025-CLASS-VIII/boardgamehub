import csv
import hashlib
import json
from io import StringIO
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import Session

from app.database import get_session
from app import crud
from app.models import BoardGame
from app.schemas import BoardGameCreate, BoardGameRead, BoardGameUpdate

router = APIRouter(prefix="/boardgames", tags=["BoardGames"])


def compute_etag(body: dict) -> str:
    digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
    return f'W/"{digest}"'


def maybe_return_not_modified(request: Request, response: Response, payload: dict) -> Response:
    etag = compute_etag(payload)
    if_none_match = request.headers.get("if-none-match")
    if if_none_match == etag:
        not_modified = Response(status_code=304)
        not_modified.headers["ETag"] = etag
        return not_modified
    response.headers["ETag"] = etag
    return response


def stream_as_csv(payload: dict) -> StreamingResponse:
    buffer = StringIO()
    fieldnames = ("id", "name", "rating", "year_published", "min_players", "max_players", "playtime_minutes", "complexity")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    # Pydantic models need to be converted to dicts if they aren't already
    for item in payload["items"]:
        writer.writerow(item if isinstance(item, dict) else item.model_dump())
    buffer.seek(0)
    headers = {
        "Content-Type": "text/csv",
        "Content-Disposition": 'attachment; filename="boardgames.csv"',
        "X-Total-Count": str(payload["total"]),
    }
    return StreamingResponse(iter([buffer.getvalue()]), headers=headers)


@router.get("/")
def list_boardgames(
    request: Request,
    response: Response,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    format: Literal["json", "csv"] = Query("json"),
    session: Session = Depends(get_session),
):
    offset = (page - 1) * page_size
    items, total = crud.list_boardgames(session, offset=offset, limit=page_size)
    
    # Convert Pydantic models to dicts for JSON serialization/hashing
    items_dicts = [item.model_dump() for item in items]
    
    payload = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items_dicts,
    }

    if format == "csv":
        return stream_as_csv(payload)

    response = JSONResponse(payload, headers={"X-Total-Count": str(total)})
    return maybe_return_not_modified(request, response, payload)


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
