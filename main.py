from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

from database.db import init_db
from services.scheduler import start_scheduler, stop_scheduler
from api.routes import router

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Nigerian Security News Platform",
    description="Automated extraction of security-related news from Nigerian sources",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database and start scheduler on app startup.
    """
    logger.info("Starting Nigerian Security News Platform")
    init_db()
    logger.info("Database initialized")
    start_scheduler()
    logger.info("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Stop scheduler on app shutdown.
    """
    logger.info("Shutting down application")
    stop_scheduler()


@app.get("/", tags=["root"])
def read_root():
    """
    Welcome endpoint.
    """
    return {
        "name": "Nigerian Security News Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "articles": "/api/articles",
            "statistics": "/api/statistics",
            "sources": "/api/sources",
            "incident_types": "/api/incident-types",
            "locations": "/api/locations",
            "scrape_now": "/api/scrape-now"
        }
    }


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
