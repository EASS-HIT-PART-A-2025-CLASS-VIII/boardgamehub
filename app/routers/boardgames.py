import csv
import hashlib
import json
from io import StringIO
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import Session

from app.database import get_session
from app import crud
from app.models import BoardGame
from app.schemas import BoardGameCreate, BoardGameRead, BoardGameUpdate
from sqlmodel import select, func
from app.limiter import limiter
from app.security import require_role

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
@limiter.limit("5/minute")
def list_boardgames(
    request: Request,
    response: Response,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    format: Literal["json", "csv"] = Query("json"),
    search: str | None = Query(None),
    min_players: int | None = Query(None),
    max_players: int | None = Query(None),
    session: Session = Depends(get_session),
):
    offset = (page - 1) * page_size
    items, total = crud.list_boardgames(
        session, 
        offset=offset, 
        limit=page_size,
        search=search,
        min_players=min_players,
        max_players=max_players,
    )
    
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
def create_boardgame(
    payload: BoardGameCreate, 
    session: Session = Depends(get_session),
    _claims=Depends(require_role("admin")),
):
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
    _claims=Depends(require_role("admin")),
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
def delete_boardgame(
    boardgame_id: int, 
    session: Session = Depends(get_session),
    _claims=Depends(require_role("admin")),
):
    ok = crud.delete_boardgame(session, boardgame_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Board game not found")
    return None


@router.post("/upload", status_code=201)
async def upload_boardgames(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    _claims=Depends(require_role("admin")),
):
    """
    Upload a CSV file containing board games data from BGG dataset.
    """
    filename = file.filename or ""
    if not filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    try:
        # Decode bytes to string
        decoded_content = content.decode("utf-8")
        # Use StringIO to create file-like object for csv reader
        csv_file = StringIO(decoded_content)
        csv_reader = csv.DictReader(csv_file, delimiter=";")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse CSV file.")

    added_count = 0
    errors = []

    # Pre-fetch existing game names to avoid N+1 queries
    # Using lowercase for case-insensitive comparison
    existing_names_query = select(func.lower(BoardGame.name))
    existing_names = set(session.exec(existing_names_query).all())

    new_games = []

    # Process rows
    for row in csv_reader:
        try:
            name = row.get("Name")
            if not name:
                continue

            name_lower = name.strip().lower()
            if name_lower in existing_names:
                continue
            
            # Add to local cache to prevent duplicates within the same CSV
            existing_names.add(name_lower)

            # Parse numeric fields with defaults
            try:
                # Helper for safer parsing
                def get_int(key: str, default: int | None = 0) -> int | None:
                    val = row.get(key)
                    if val and val.strip():
                        return int(val.strip())
                    return default

                year = get_int("Year Published", None)
                min_players = get_int("Min Players") or 0
                max_players = get_int("Max Players") or 0
                play_time = get_int("Play Time") or 0
                
                # Handle comma decimal format 
                complexity_val = row.get("Complexity Average", "0")
                complexity_str = complexity_val.replace(",", ".") if complexity_val else "0"
                complexity = float(complexity_str)
                
                rating_val = row.get("Rating Average", "0")
                rating_str = rating_val.replace(",", ".") if rating_val else "0"
                rating = float(rating_str)
            except ValueError:
                errors.append(f"Skipped row {row.get('ID', '?')}: Invalid numeric format")
                continue

            game = BoardGame(
                name=name,
                year_published=year,
                min_players=min_players,
                max_players=max_players,
                play_time_min=play_time,
                complexity=complexity,
                rating=rating,
                designer=None # Designer not in this CSV format
            )
            new_games.append(game)
            added_count += 1
            
        except Exception as e:
            errors.append(f"Error processing row {row.get('ID', 'unknown')}: {str(e)}")

    # Bulk insert
    try:
        # Commit in chunks if necessary, but 20k rows is usually fine for one commit in typical SQL
        # Using add_all is faster than individual adds
        session.add_all(new_games)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {
        "message": f"Successfully added {added_count} games", 
        "errors": errors[:10]  # Return first 10 errors to avoid huge response
    }
