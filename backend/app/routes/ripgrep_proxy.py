"""
Ripgrep API Proxy Route

This proxy allows Postman Actions (running in cloud) to call Ripgrep API
through the same ngrok tunnel as the backend (port 8000).

Why needed: ngrok can only tunnel ONE port, so we proxy:
  Postman → ngrok:8000/api/ripgrep/search → localhost:3001/api/search

This way Postman only needs to know one URL!
"""

import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

router = APIRouter()

# Ripgrep API configuration
RIPGREP_API_URL = os.getenv("RIPGREP_API_URL", "http://localhost:3001")


class RipgrepSearchRequest(BaseModel):
    """Request model for Ripgrep search proxy"""
    query: str
    path: Optional[str] = "./"
    type: Optional[str] = "all"
    case_sensitive: Optional[bool] = False


@router.post("/ripgrep/search")
async def proxy_ripgrep_search(request: RipgrepSearchRequest) -> Dict[str, Any]:
    """
    Proxy endpoint for Ripgrep API search.

    Forwards requests from Postman Action (via ngrok) to local Ripgrep API.

    Example:
        POST /api/ripgrep/search
        {
            "query": "ProfileCard",
            "path": "./",
            "type": "tsx"
        }

    Returns:
        Same response as Ripgrep API:
        {
            "success": true,
            "data": {
                "files": ["src/components/ProfileCard.tsx"],
                "total": 1,
                "is_new_feature": false,
                "message": "Found existing files..."
            }
        }
    """
    try:
        # Forward request to Ripgrep API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RIPGREP_API_URL}/api/search",
                json={
                    "query": request.query,
                    "path": request.path,
                    "type": request.type,
                    "case_sensitive": request.case_sensitive,
                },
                timeout=10.0
            )

            # Check if Ripgrep API is healthy
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Ripgrep API returned {response.status_code}: {response.text}"
                )

            # Return Ripgrep response as-is
            return response.json()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ripgrep API at {RIPGREP_API_URL}. Is it running? (npm run dev in ripgrep-api/)"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Ripgrep API request timed out (>10s)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Proxy error: {str(e)}"
        )


@router.get("/ripgrep/health")
async def proxy_ripgrep_health() -> Dict[str, Any]:
    """
    Health check endpoint for Ripgrep API proxy.

    Returns:
        {
            "proxy_status": "healthy",
            "ripgrep_api_url": "http://localhost:3001",
            "ripgrep_api_status": "healthy" | "unreachable"
        }
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RIPGREP_API_URL}/api/health",
                timeout=5.0
            )

            return {
                "proxy_status": "healthy",
                "ripgrep_api_url": RIPGREP_API_URL,
                "ripgrep_api_status": "healthy" if response.status_code == 200 else "error",
                "ripgrep_response": response.json() if response.status_code == 200 else None
            }

    except httpx.ConnectError:
        return {
            "proxy_status": "healthy",
            "ripgrep_api_url": RIPGREP_API_URL,
            "ripgrep_api_status": "unreachable",
            "error": "Cannot connect to Ripgrep API. Start it with: npm run dev"
        }
    except Exception as e:
        return {
            "proxy_status": "healthy",
            "ripgrep_api_url": RIPGREP_API_URL,
            "ripgrep_api_status": "error",
            "error": str(e)
        }
