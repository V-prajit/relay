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


# Import and include routers

# Snowflake routes
try:
    from app.routes import snowflake
    app.include_router(snowflake.router, prefix="/api")
    print("✓ Snowflake routes loaded")
except ImportError as e:
    print(f"⚠ Snowflake routes not loaded: {e}")
except Exception as e:
    print(f"⚠ Error loading Snowflake routes: {e}")

# Dashboard routes
try:
    from app.routes import dashboard
    app.include_router(dashboard.router, prefix="/api")
    print("✓ Dashboard routes loaded")
except ImportError as e:
    print(f"⚠ Dashboard routes not loaded: {e}")
except Exception as e:
    print(f"⚠ Error loading Dashboard routes: {e}")

# Cortex Showcase routes
try:
    from app.routes import cortex_showcase
    app.include_router(cortex_showcase.router, prefix="/api")
    print("✓ Cortex Showcase routes loaded")
except ImportError as e:
    print(f"⚠ Cortex Showcase routes not loaded: {e}")
except Exception as e:
    print(f"⚠ Error loading Cortex Showcase routes: {e}")

# Ripgrep Proxy routes (for Postman Action via ngrok)
try:
    from app.routes import ripgrep_proxy
    app.include_router(ripgrep_proxy.router, prefix="/api")
    print("✓ Ripgrep Proxy routes loaded (Postman can now call /api/ripgrep/search)")
except ImportError as e:
    print(f"⚠ Ripgrep Proxy routes not loaded: {e}")
except Exception as e:
    print(f"⚠ Error loading Ripgrep Proxy routes: {e}")

# GitHub routes (for creating PRs and issues)
try:
    from app.routes import github
    app.include_router(github.router, prefix="/api")
    print("✓ GitHub routes loaded (PR creation enabled)")
except ImportError as e:
    print(f"⚠ GitHub routes not loaded: {e}")
except Exception as e:
    print(f"⚠ Error loading GitHub routes: {e}")
