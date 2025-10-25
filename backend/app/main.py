"""
BugRewind API - FastAPI backend for git archaeology and bug analysis

This is the main entry point for the FastAPI application.
"""

import os
from pathlib import Path
from typing import Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown tasks.

    Replaces the deprecated @app.on_event("startup") pattern.
    """
    # Startup tasks
    clone_dir = os.getenv("CLONE_DIR", "/tmp/bugrewind-clones")
    Path(clone_dir).mkdir(parents=True, exist_ok=True)

    port = os.getenv("PORT", "8000")

    print("=" * 60)
    print("BugRewind API Starting")
    print("=" * 60)
    print(f"Clone directory: {clone_dir}")
    print(f"Server port: {port}")
    print(f"API documentation: http://localhost:{port}/docs")
    print(f"Alternative docs: http://localhost:{port}/redoc")
    print("=" * 60)

    yield  # Server runs here

    # Shutdown tasks (if needed)
    print("BugRewind API shutting down")


# Initialize FastAPI app with lifespan handler
app = FastAPI(
    title="BugRewind API",
    version="1.0.0",
    description="Git archaeology for bug origins - trace bugs back to their source commits",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: Status and version information
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "BugRewind API"
    }


# Import and include routers (we'll add these as we build them)
# from app.routes import analyze
# app.include_router(analyze.router, prefix="/api", tags=["analysis"])
