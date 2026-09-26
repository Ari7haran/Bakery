from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal, init_db_indexes
from app.core.exceptions import register_exception_handlers
from app.api.router import api_router
from app.utils.seed_data import seed_database

logger = logging.getLogger(__name__)

# Create tables if not present and initialize indexes
Base.metadata.create_all(bind=engine)
init_db_indexes(engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration (Restricted allowed origins for credentials security)
cors_origins = (
    settings.BACKEND_CORS_ORIGINS
    if isinstance(settings.BACKEND_CORS_ORIGINS, list)
    else ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom domain exception handlers
register_exception_handlers(app)

# Global unhandled exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception during {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."},
    )

# Include Centralized API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "message": "Welcome to Sweet Crumbs Bakery API 🥐✨",
        "docs": "/docs",
        "version": settings.VERSION
    }
