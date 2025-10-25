"""
BugRewind API Server Runner

Use this script to start the FastAPI development server.

Usage:
    python run.py

Environment Variables:
    PORT - Server port (default: 8000)
    All other variables loaded from .env file
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

if __name__ == "__main__":
    # Get port from environment
    port = int(os.getenv("PORT", 8000))

    # Run the server with uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload during development
        reload_dirs=["app"]  # Only watch the app directory
    )
