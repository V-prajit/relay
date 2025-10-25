"""FastAPI server for BugRewind PM Copilot API.

Exposes Elasticsearch-backed tools for:
- Hybrid search (BM25 + kNN + ELSER)
- Graph exploration (co-change networks)
- Impact analysis (code ownership, risk)
- GitHub PR creation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from app.config import config
from app.elastic.client import elastic_client
from app.elastic.search import hybrid_searcher
from app.elastic.graph import graph_explorer
from app.elastic.files_indexer import files_indexer
from app.embeddings.client import embedding_client


# FastAPI app
app = FastAPI(
    title="BugRewind PM Copilot API",
    description="Elasticsearch-powered impact analysis and code archaeology",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    repo_id: Optional[str] = None
    size: int = 10
    time_range_months: Optional[int] = None


class GraphRequest(BaseModel):
    files: List[str]
    repo_id: Optional[str] = None
    max_depth: int = 2
    max_connections: int = 20


class ImpactRequest(BaseModel):
    file_path: str
    repo_id: str
    min_co_change_score: float = 0.3


class PRRequest(BaseModel):
    repo_url: str
    branch_name: str
    file_path: str
    patch_content: str
    title: str
    description: str


# Health Check
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint - verifies Elasticsearch connection."""
    try:
        elastic_connected = elastic_client.ping()
        return {
            "status": "ok" if elastic_connected else "degraded",
            "elastic_connected": elastic_connected,
            "elastic_endpoint": config.ELASTIC_ENDPOINT,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "elastic_connected": False,
            "error": str(e)
        }


# Hybrid Search Endpoint
@app.post("/api/search")
async def search_commits(request: SearchRequest) -> Dict[str, Any]:
    """
    Hybrid search using BM25 + kNN + ELSER.

    Combines:
    - BM25: Keyword matching
    - kNN: Semantic similarity via dense vectors
    - ELSER: Learned sparse embeddings for explainable search

    Returns commits ranked by RRF (Reciprocal Rank Fusion).
    """
    try:
        # Generate query embedding
        query_vector = embedding_client.embed_text(request.query)

        # Hybrid search
        results = hybrid_searcher.hybrid_search(
            query_text=request.query,
            query_vector=query_vector,
            repo_id=request.repo_id,
            size=request.size,
            time_range_months=request.time_range_months
        )

        # Format response
        hits = []
        for hit in results['hits']['hits']:
            fields = hit.get('fields', {})
            hits.append({
                'sha': fields.get('sha', [''])[0],
                'message': fields.get('message', [''])[0],
                'author': fields.get('author_name', ['Unknown'])[0],
                'date': fields.get('commit_date', [''])[0],
                'files_changed': fields.get('files_changed.path', []),
                'score': hit.get('_score', 0),
                'rank': hit.get('_rank', 0)
            })

        # Extract aggregations
        aggs = results.get('aggregations', {})
        impacted_files = []
        if 'impacted_files' in aggs:
            file_buckets = aggs['impacted_files'].get('file_paths', {}).get('buckets', [])
            impacted_files = [
                {'file': bucket['key'], 'count': bucket['doc_count']}
                for bucket in file_buckets[:10]
            ]

        top_authors = []
        if 'top_authors' in aggs:
            author_buckets = aggs['top_authors'].get('buckets', [])
            top_authors = [
                {'author': bucket['key'], 'commits': bucket['doc_count']}
                for bucket in author_buckets[:5]
            ]

        return {
            'total': results['hits']['total']['value'],
            'hits': hits,
            'aggregations': {
                'impacted_files': impacted_files,
                'top_authors': top_authors
            },
            'query': request.query,
            'search_type': 'hybrid_bm25_knn_elser'
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Graph Exploration Endpoint
@app.post("/api/graph")
async def explore_graph(request: GraphRequest) -> Dict[str, Any]:
    """
    Explore co-change network using Elasticsearch Graph API.

    Returns files that frequently change together with the seed files.
    Uses significance scoring to surface unexpected connections.
    """
    try:
        graph = graph_explorer.explore_co_change_network(
            start_files=request.files,
            repo_id=request.repo_id,
            max_depth=request.max_depth,
            max_connections=request.max_connections
        )

        return {
            'vertices': graph['vertices'],
            'connections': graph['connections'],
            'took_ms': graph.get('took_ms', 0),
            'seed_files': request.files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph exploration failed: {str(e)}")


# Impact Analysis Endpoint
@app.post("/api/impact")
async def get_impact_set(request: ImpactRequest) -> Dict[str, Any]:
    """
    Get impact set for a file: owners, co-change files, tests, risk.

    Returns:
    - Top-3 code owners
    - Related files (co-change score > threshold)
    - Test dependencies
    - Risk metrics (churn, ownership)
    """
    try:
        impact = files_indexer.get_impact_set(
            file_path=request.file_path,
            repo_id=request.repo_id,
            min_co_change_score=request.min_co_change_score
        )

        if not impact:
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

        return {
            'file_path': impact['file_path'],
            'owners': impact['owners'],
            'related_files': impact['related_files'],
            'test_dependencies': impact.get('test_dependencies', []),
            'recent_churn': impact.get('recent_churn', 0),
            'risk_level': 'high' if impact.get('recent_churn', 0) > 5 else 'medium' if impact.get('recent_churn', 0) > 2 else 'low'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impact analysis failed: {str(e)}")


# GitHub PR Creation Endpoint
@app.post("/api/create-pr")
async def create_pull_request(request: PRRequest) -> Dict[str, Any]:
    """
    Create a GitHub pull request with bug fix.

    Requires GITHUB_TOKEN in environment.
    """
    try:
        from app.github.pr_creator import pr_creator

        result = pr_creator.create_fix_pr(
            repo_url=request.repo_url,
            branch_name=request.branch_name,
            file_path=request.file_path,
            patch_content=request.patch_content,
            title=request.title,
            description=request.description
        )

        return result

    except ImportError:
        raise HTTPException(status_code=501, detail="GitHub integration not configured")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PR creation failed: {str(e)}")


# Root endpoint
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "BugRewind PM Copilot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "search": "POST /api/search",
            "graph": "POST /api/graph",
            "impact": "POST /api/impact",
            "create_pr": "POST /api/create-pr"
        }
    }


# Run server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=True,
        log_level="info"
    )
