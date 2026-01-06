from fastapi import APIRouter
from sqlmodel import Session, text

from app.database import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    db_status = "ok"

    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "database": db_status,
    }
