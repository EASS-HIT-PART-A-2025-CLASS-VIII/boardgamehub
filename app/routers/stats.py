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


def _player_bucket(max_players: int) -> str:
    if max_players <= 2:
        return "1-2"
    if max_players <= 4:
        return "3-4"
    return "5+"


def _compute_snapshot(games) -> StatsSnapshot:
    total = len(games)

    ratings = [g.rating for g in games if g.rating is not None]
    complexities = [g.complexity for g in games if g.complexity is not None]

    player_counts: dict[str, int] = {"1-2": 0, "3-4": 0, "5+": 0}
    for g in games:
        player_counts[_player_bucket(g.max_players)] += 1

    top = sorted(
        [g for g in games if g.rating is not None],
        key=lambda x: x.rating,
        reverse=True,
    )[:5]
    top_items = [TopRatedItem(id=g.id, name=g.name, rating=float(g.rating)) for g in top]

    return StatsSnapshot(
        total_games=total,
        avg_rating=(sum(ratings) / len(ratings)) if ratings else None,
        avg_complexity=(sum(complexities) / len(complexities)) if complexities else None,
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