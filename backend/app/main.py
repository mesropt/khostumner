from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connection pool created on first use;
    # migrations run via alembic upgrade head BEFORE uvicorn starts in Docker
    yield
    # Shutdown: dispose connection pool cleanly
    await engine.dispose()


app = FastAPI(
    title="Khostumner API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
