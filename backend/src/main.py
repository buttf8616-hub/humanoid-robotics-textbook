"""FastAPI application entry point."""
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.api.auth_routes import auth_router
from src.api.content_routes import content_router
from src.db.database import init_db

app = FastAPI(
    title="Book Ingestion Pipeline",
    description="RAG ingestion pipeline for Physical AI & Humanoid Robotics book",
    version="0.1.0",
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database on startup
init_db()

# Register API routes
app.include_router(router, prefix="/api/v1", tags=["ingestion"])
app.include_router(auth_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }
