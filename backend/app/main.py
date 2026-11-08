from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.core.database import Base, check_db_connection, engine
from app.courses.router import router as courses_router
from app.quizzes.router import results_router
from app.quizzes.router import router as quizzes_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description="REST API for SmartLearn: courses, learning materials and practice quizzes.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(quizzes_router)
app.include_router(results_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    try:
        check_db_connection()
        database = "connected"
    except Exception:
        database = "unavailable"
    return {"status": "ok", "database": database}
