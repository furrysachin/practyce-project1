"""
Retail Banking Transaction Analytics - FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import engine, Base
from models import Batch, Customer, Account, Merchant, Transaction, Balance, Metadata  # noqa: F401 - register models
from routes.upload import router as upload_router
from routes.summary import router as summary_router

app = FastAPI(
    title="Retail Banking Transaction Analytics API",
    description="Ingest JSON transaction files, store in PostgreSQL, serve analytics summaries",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix=settings.API_PREFIX)
app.include_router(summary_router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {"service": "Retail Banking Transaction Analytics", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


def init_db():
    """Create tables if they do not exist (for dev). Prefer running schema.sql for production."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
