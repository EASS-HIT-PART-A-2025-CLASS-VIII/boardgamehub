import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session

from app.database import get_session
from app import crud
from app.redis_client import get_redis_client
from app.schemas import StatsSnapshot, TopRatedItem
from app.security import require_role   
import redis.asyncio as redis

router = APIRouter(tags=["Stats"])

STATS_SNAPSHOT_KEY = "stats:snapshot"
IDEMPOTENCY_PREFIX = "idempotency:stats:"


def _player_bucket(val: int | None) -> str:
    if val is None:
        return "1-2"
    if val <= 2:
        return "1-2"
    if val <= 4:
        return "3-4"
    return "5+"


def _compute_snapshot(games) -> StatsSnapshot:
    total = len(games)
    
    # Filter for valid values
    valid_ratings = [g.rating for g in games if g.rating is not None]
    valid_complexities = [g.complexity for g in games if g.complexity is not None]

    calc_avg_rating = (sum(valid_ratings) / len(valid_ratings)) if valid_ratings else 0.0
    calc_avg_complexity = (sum(valid_complexities) / len(valid_complexities)) if valid_complexities else 0.0

    player_counts = {"1-2": 0, "3-4": 0, "5+": 0}
    for g in games:
        bucket = _player_bucket(g.max_players)
        player_counts[bucket] += 1

    # Top games by rating (must have rating)
    valid_games_for_top = [g for g in games if g.rating is not None]
    top = sorted(valid_games_for_top, key=lambda x: x.rating, reverse=True)[:5]
    
    top_items = []
    for g in top:
        top_items.append(
            TopRatedItem(id=g.id, name=g.name, rating=float(g.rating))
        )

    return StatsSnapshot(
        total_games=total,
        avg_rating=calc_avg_rating,
        avg_complexity=calc_avg_complexity,
        player_range_counts=player_counts,
        top_rated=top_items,
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/stats", response_model=StatsSnapshot)
async def get_stats(r: redis.Redis = Depends(get_redis_client)):
    raw = await r.get(STATS_SNAPSHOT_KEY)
    if not raw:
        raise HTTPException(status_code=404, detail="Stats not generated yet. Run refresh.")
    return StatsSnapshot(**json.loads(raw))


@router.post("/internal/stats/refresh")
async def refresh_stats(
    session: Session = Depends(get_session),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
    _claims=Depends(require_role("admin")), 
    r: redis.Redis = Depends(get_redis_client),  
):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key header")

    idem_key = f"{IDEMPOTENCY_PREFIX}{idempotency_key}"

    if await r.exists(idem_key):
        return {"status": "already_done", "idempotency_key": idempotency_key}

    games, _ = crud.list_boardgames(session, limit=10000)
    snapshot = _compute_snapshot(games)

    await r.set(STATS_SNAPSHOT_KEY, json.dumps(snapshot.model_dump(mode="json")))
    await r.setex(idem_key, 60 * 60 * 48, "1")

    return {
        "status": "updated",
        "idempotency_key": idempotency_key,
        "generated_at": snapshot.generated_at.isoformat(),
        "trace_id": trace_id,
    }