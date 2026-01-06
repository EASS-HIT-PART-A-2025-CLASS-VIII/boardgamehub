from fastapi import FastAPI
from sqlmodel import Session, text
from starlette import status
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


from app.database import create_db_and_tables, engine
from app.routers.boardgames import router as boardgames_router

app = FastAPI(title="BoardGameHub API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit local
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/health")
def health():
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "ok", "database": "error"},
        )


app.include_router(boardgames_router)
