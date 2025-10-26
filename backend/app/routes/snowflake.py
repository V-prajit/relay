"""
Snowflake API routes for BugRewind

Provides REST API endpoints for:
- Commit search and storage
- Cortex AI features (LLM functions, semantic search)
- Analytics and statistics
- Time Travel queries
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from app.services.snowflake_service import SnowflakeService
from app.models.requests import GeneratePRRequest

# Create router
router = APIRouter(prefix="/snowflake", tags=["snowflake"])


# ==================== REQUEST/RESPONSE MODELS ====================

class CommitInsertRequest(BaseModel):
    """Request model for inserting commits."""
    commit_hash: str
    repo_name: str
    author: str
    author_email: Optional[str] = ""
    timestamp: str
    message: str
    files_changed: List[str] = []
    insertions: int = 0
    deletions: int = 0


class BulkCommitInsertRequest(BaseModel):
    """Request model for bulk commit insertion."""
    repo_name: str
    commits: List[Dict[str, Any]]


class BugAnalysisRequest(BaseModel):
    """Request model for storing bug analysis."""
    repo_name: str
    bug_description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    first_bad_commit: Optional[str] = None
    root_cause: Optional[str] = None
    developer_intent: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: Optional[float] = None
    ai_model: Optional[str] = "claude-sonnet-4"
    execution_time_ms: Optional[int] = None


class CortexCompleteRequest(BaseModel):
    """Request model for Cortex COMPLETE function."""
    prompt: str
    model: str = "mistral-large"


# ==================== HEALTH & STATUS ====================

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Check Snowflake connection health.

    Returns connection status, database info, and version.
    """
    snowflake = SnowflakeService.get_instance()
    return snowflake.health_check()


# ==================== COMMIT OPERATIONS ====================

@router.post("/commits")
async def insert_commit(commit: CommitInsertRequest) -> Dict[str, Any]:
    """
    Insert a single commit into Snowflake.

    Example:
    ```json
    {
      "commit_hash": "abc123...",
      "repo_name": "myorg/myrepo",
      "author": "John Doe",
      "author_email": "john@example.com",
      "timestamp": "2024-01-15T10:30:00",
      "message": "Fix authentication bug",
      "files_changed": ["src/auth.py", "tests/test_auth.py"],
      "insertions": 15,
      "deletions": 8
    }
    ```
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    success = snowflake.insert_commit(commit.dict())

    if success:
        return {
            "success": True,
            "message": "Commit inserted successfully",
            "commit_hash": commit.commit_hash
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to insert commit")


@router.post("/commits/bulk")
async def bulk_insert_commits(request: BulkCommitInsertRequest) -> Dict[str, Any]:
    """
    Bulk insert multiple commits.

    Example:
    ```json
    {
      "repo_name": "myorg/myrepo",
      "commits": [
        {
          "commit_hash": "abc123...",
          "author": "John",
          "message": "Fix bug",
          ...
        },
        ...
      ]
    }
    ```
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    count = snowflake.bulk_insert_commits(request.commits, request.repo_name)

    return {
        "success": True,
        "inserted_count": count,
        "total_count": len(request.commits),
        "repo_name": request.repo_name
    }


@router.get("/commits/search")
async def search_commits(
    repo_name: str,
    keyword: Optional[str] = None,
    author: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(default=20, le=100)
) -> Dict[str, Any]:
    """
    Search commits with filters.

    Query parameters:
    - repo_name: Repository name (required)
    - keyword: Search in commit messages
    - author: Filter by author name
    - from_date: Start date (ISO format: 2024-01-01)
    - to_date: End date (ISO format: 2024-12-31)
    - limit: Max results (default 20, max 100)

    Example:
    `/snowflake/commits/search?repo_name=myrepo&keyword=auth&limit=10`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    results = snowflake.search_commits(
        repo_name=repo_name,
        keyword=keyword,
        author=author,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )

    return {
        "total": len(results),
        "results": results,
        "filters": {
            "repo_name": repo_name,
            "keyword": keyword,
            "author": author,
            "from_date": from_date,
            "to_date": to_date
        }
    }


# ==================== CORTEX LLM FUNCTIONS ====================

@router.post("/cortex/complete")
async def cortex_complete(request: CortexCompleteRequest) -> Dict[str, Any]:
    """
    Use Snowflake Cortex COMPLETE function for AI text generation.

    Models available:
    - mistral-large (default)
    - llama3-70b
    - mixtral-8x7b
    - reka-flash

    Example:
    ```json
    {
      "prompt": "Explain what this commit does: 'Fix null pointer in auth'",
      "model": "mistral-large"
    }
    ```
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    response = snowflake.cortex_complete(request.prompt, request.model)

    if not response:
        raise HTTPException(status_code=500, detail="Cortex COMPLETE failed")

    return {
        "prompt": request.prompt,
        "model": request.model,
        "response": response
    }


@router.get("/cortex/sentiment/{commit_id}")
async def analyze_sentiment(commit_id: str) -> Dict[str, Any]:
    """
    Analyze commit message sentiment using Cortex SENTIMENT.

    Returns sentiment score (-1 to 1), label, and panic fix detection.

    Example: `/snowflake/cortex/sentiment/abc123...`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    result = snowflake.analyze_commit_sentiment(commit_id)

    if not result:
        raise HTTPException(status_code=404, detail="Commit not found or sentiment analysis failed")

    return result


@router.get("/cortex/summarize/{commit_id}")
async def summarize_commit(commit_id: str) -> Dict[str, Any]:
    """
    Summarize commit message using Cortex SUMMARIZE.

    Example: `/snowflake/cortex/summarize/abc123...`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    summary = snowflake.summarize_commit_message(commit_id)

    if not summary:
        raise HTTPException(status_code=404, detail="Commit not found or summarization failed")

    return {
        "commit_id": commit_id,
        "summary": summary
    }


@router.get("/cortex/extract/{commit_id}")
async def extract_from_commit(
    commit_id: str,
    question: str = Query(..., description="Question to extract answer for")
) -> Dict[str, Any]:
    """
    Extract specific information from commit using Cortex EXTRACT_ANSWER.

    Example:
    `/snowflake/cortex/extract/abc123?question=What bug was fixed?`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    answer = snowflake.extract_bug_info_from_commit(commit_id, question)

    if not answer:
        raise HTTPException(status_code=404, detail="Commit not found or extraction failed")

    return {
        "commit_id": commit_id,
        "question": question,
        "answer": answer
    }


# ==================== CORTEX SEARCH ====================

@router.get("/cortex/search")
async def cortex_search(
    query: str,
    repo_name: Optional[str] = None,
    limit: int = Query(default=10, le=50)
) -> Dict[str, Any]:
    """
    Semantic search through commits using Cortex Search.

    This is better than keyword search - it understands intent!

    Example:
    `/snowflake/cortex/search?query=authentication bug fix&repo_name=myrepo&limit=5`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    results = snowflake.cortex_search_commits(query, repo_name, limit)

    return {
        "query": query,
        "repo_name": repo_name,
        "total": len(results),
        "results": results
    }


# ==================== BUG ANALYSIS ====================

@router.post("/analysis")
async def store_analysis(analysis: BugAnalysisRequest) -> Dict[str, Any]:
    """
    Store bug analysis results in Snowflake.

    Example:
    ```json
    {
      "repo_name": "myorg/myrepo",
      "bug_description": "Auth fails with 401",
      "file_path": "src/auth.py",
      "line_number": 45,
      "first_bad_commit": "abc123...",
      "root_cause": "Removed null check",
      "confidence": 0.92
    }
    ```
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    analysis_id = snowflake.store_bug_analysis(analysis.dict())

    if not analysis_id:
        raise HTTPException(status_code=500, detail="Failed to store analysis")

    return {
        "success": True,
        "analysis_id": analysis_id,
        "repo_name": analysis.repo_name
    }


@router.get("/analysis/history")
async def get_analysis_history(
    repo_name: str,
    limit: int = Query(default=50, le=200)
) -> Dict[str, Any]:
    """
    Get historical bug analyses for a repository.

    Example: `/snowflake/analysis/history?repo_name=myrepo&limit=20`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    results = snowflake.get_bug_analysis_history(repo_name, limit)

    return {
        "repo_name": repo_name,
        "total": len(results),
        "analyses": results
    }


# ==================== PR GENERATION (HYBRID AI) ====================

@router.post("/generate-pr")
async def generate_pr(request: GeneratePRRequest) -> Dict[str, Any]:
    """
    Generate PR content using Snowflake Cortex LLM.

    This endpoint is called BY Postman AI Agent as a tool.
    - AI Agent decides WHEN to call this (orchestration)
    - Cortex decides WHAT code to generate (execution)

    Example:
    ```json
    {
      "feature_request": "fix mobile login responsive design",
      "impacted_files": ["src/pages/Login.tsx"],
      "is_new_feature": false,
      "repo_name": "V-prajit/youareabsolutelyright",
      "conflict_info": "Conflicts with PR #42 (1 file overlap)"
    }
    ```

    Returns:
    ```json
    {
      "success": true,
      "pr_title": "fix: Mobile login responsive design",
      "pr_description": "...",
      "branch_name": "pm-copilot/fix-mobile-login-20251026-abc123",
      "generated_by": "Snowflake Cortex (mistral-large)",
      "execution_time_ms": 2500,
      "hybrid_ai": {
        "orchestrator": "Postman AI Agent (GPT-5)",
        "generator": "Snowflake Cortex (Mistral-Large)"
      }
    }
    ```
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Snowflake is not connected. Check ENABLE_SNOWFLAKE=true and credentials."
        )

    try:
        result = snowflake.generate_pr_with_cortex(
            feature_request=request.feature_request,
            impacted_files=request.impacted_files,
            is_new_feature=request.is_new_feature,
            repo_name=request.repo_name,
            conflict_info=request.conflict_info
        )

        return {
            "success": True,
            "pr_title": result["pr_title"],
            "pr_description": result["pr_description"],
            "branch_name": result["branch_name"],
            "generated_by": result["generated_by"],
            "execution_time_ms": result["execution_time_ms"],
            "model": result["model"],
            "hybrid_ai": {
                "orchestrator": "Postman AI Agent (GPT-5)",
                "generator": f"Snowflake Cortex ({result['model']})",
                "architecture": "AI Agent orchestrates, Cortex executes"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PR with Cortex: {str(e)}"
        )


# ==================== ANALYTICS ====================

@router.get("/analytics/panic-fixes")
async def get_panic_fixes(
    repo_name: str,
    days: int = Query(default=30, ge=1, le=365)
) -> Dict[str, Any]:
    """
    Find commits that are likely panic fixes (very negative sentiment).

    These indicate areas that frequently need urgent fixes.

    Example: `/snowflake/analytics/panic-fixes?repo_name=myrepo&days=30`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    results = snowflake.get_panic_fixes(repo_name, days)

    return {
        "repo_name": repo_name,
        "time_period_days": days,
        "panic_fix_count": len(results),
        "panic_fixes": results
    }


@router.get("/analytics/stats")
async def get_repo_stats(repo_name: str) -> Dict[str, Any]:
    """
    Get statistics for a repository.

    Returns: total commits, unique authors, date range, insertions/deletions.

    Example: `/snowflake/analytics/stats?repo_name=myrepo`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    stats = snowflake.get_repository_stats(repo_name)

    if not stats:
        raise HTTPException(status_code=404, detail="Repository not found or has no data")

    return {
        "repo_name": repo_name,
        "statistics": stats
    }


# ==================== TIME TRAVEL ====================

@router.get("/time-travel/{table}")
async def time_travel_query(
    table: str,
    timestamp: str = Query(..., description="ISO timestamp to query at"),
    conditions: str = Query(default="1=1", description="WHERE clause conditions")
) -> Dict[str, Any]:
    """
    Query historical data using Snowflake Time Travel.

    Example:
    `/snowflake/time-travel/COMMITS?timestamp=2024-01-15T10:00:00&conditions=REPO_NAME='myrepo'`
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake is not connected")

    # Only allow specific tables for security
    allowed_tables = ["COMMITS", "BUG_ANALYSIS", "COMMIT_SENTIMENT"]
    if table.upper() not in allowed_tables:
        raise HTTPException(
            status_code=400,
            detail=f"Table must be one of: {', '.join(allowed_tables)}"
        )

    results = snowflake.query_at_timestamp(table, timestamp, conditions)

    return {
        "table": table,
        "timestamp": timestamp,
        "conditions": conditions,
        "total": len(results),
        "results": results
    }
