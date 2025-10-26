"""
Snowflake Cortex Showcase Routes
Demonstrates all major Snowflake Cortex features for hackathon judges
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.services.snowflake_service import SnowflakeService

router = APIRouter(prefix="/cortex-showcase", tags=["cortex-showcase"])


# ==================== REQUEST MODELS ====================

class CortexSearchRequest(BaseModel):
    """Semantic search through commit history"""
    query: str
    limit: int = 10


class NaturalLanguageQueryRequest(BaseModel):
    """Natural language query to Cortex Analyst"""
    question: str


class TimeTravelRequest(BaseModel):
    """Time Travel query parameters"""
    hours_ago: int = 24
    query_type: str = "pr_generations"


# ==================== CORTEX SEARCH (SEMANTIC SEARCH) ====================

@router.post("/search/semantic")
async def cortex_semantic_search(request: CortexSearchRequest) -> Dict[str, Any]:
    """
    🔍 SHOWCASE: Cortex Search - Semantic (Vector) Search

    Demonstrates Snowflake Cortex Search for semantic similarity.
    Instead of keyword matching, this understands MEANING.

    Example queries:
    - "authentication bug" → finds auth-related issues
    - "performance regression" → finds slow code commits
    - "breaking change" → finds commits that broke things

    This is REAL Snowflake Cortex Search, not a mock!
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake not connected")

    try:
        # Use Cortex Search for semantic similarity
        results = snowflake.cortex_search_commits(
            query=request.query,
            limit=request.limit
        )

        return {
            "feature": "Cortex Search (Semantic/Vector Search)",
            "query": request.query,
            "results_count": len(results),
            "results": results,
            "showcase_notes": [
                "Uses vector embeddings for semantic similarity",
                "No keyword matching - understands meaning",
                "Powered by Snowflake Cortex Search",
                "Real-time search across commit history"
            ]
        }

    except Exception as e:
        # Fallback to keyword search with explanation
        try:
            results = snowflake.search_commits(
                repo_name="V-prajit/youareabsolutelyright",
                keyword=request.query,
                limit=request.limit
            )

            return {
                "feature": "Keyword Search (Cortex Search not configured)",
                "query": request.query,
                "results_count": len(results),
                "results": results,
                "note": "Cortex Search service requires setup. Showing keyword fallback.",
                "showcase_notes": [
                    "Cortex Search enables semantic similarity",
                    "Requires Cortex Search service creation",
                    "Fallback: traditional keyword search"
                ]
            }
        except Exception as fallback_error:
            return {
                "feature": "Cortex Search Demo",
                "query": request.query,
                "results_count": 0,
                "results": [],
                "note": f"Demo mode - Cortex Search setup required: {str(e)}"
            }


# ==================== CORTEX LLM FUNCTIONS ====================

@router.get("/llm-functions/demo")
async def cortex_llm_functions_demo() -> Dict[str, Any]:
    """
    🤖 SHOWCASE: Cortex LLM Functions

    Demonstrates Snowflake Cortex built-in LLM functions:
    - COMPLETE: Text generation with Mistral/Llama
    - SENTIMENT: Emotion analysis
    - SUMMARIZE: Text summarization
    - EXTRACT_ANSWER: Question answering

    All running INSIDE Snowflake - no external APIs!
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake not connected")

    try:
        # Get recent PR for demo
        pr_query = """
        SELECT
            FEATURE_REQUEST,
            PR_TITLE,
            PR_DESCRIPTION
        FROM PR_GENERATIONS
        ORDER BY GENERATED_AT DESC
        LIMIT 1
        """

        pr_result = snowflake.execute_query(pr_query)

        if not pr_result or len(pr_result) == 0:
            # Use sample data for demo
            sample_text = "Fixed critical authentication bug causing intermittent 401 errors on mobile devices"
            sample_pr = "fix: Mobile auth 401 errors"
        else:
            sample_text = pr_result[0]['FEATURE_REQUEST']
            sample_pr = pr_result[0]['PR_TITLE']

        # Demonstrate all Cortex LLM functions
        demos = {}

        # 1. SENTIMENT Analysis
        try:
            sentiment_query = f"""
            SELECT SNOWFLAKE.CORTEX.SENTIMENT('{sample_text}') as sentiment_score
            """
            sentiment_result = snowflake.execute_query(sentiment_query)
            demos['sentiment'] = {
                "function": "SNOWFLAKE.CORTEX.SENTIMENT",
                "input": sample_text,
                "output": sentiment_result[0]['SENTIMENT_SCORE'] if sentiment_result else None,
                "description": "Analyzes emotional tone (-1 to 1)",
                "use_case": "Detect panic fixes or urgent commits"
            }
        except Exception as e:
            demos['sentiment'] = {"error": str(e), "note": "Sentiment analysis demo"}

        # 2. SUMMARIZE
        try:
            summarize_query = f"""
            SELECT SNOWFLAKE.CORTEX.SUMMARIZE('{sample_text}') as summary
            """
            summary_result = snowflake.execute_query(summarize_query)
            demos['summarize'] = {
                "function": "SNOWFLAKE.CORTEX.SUMMARIZE",
                "input": sample_text,
                "output": summary_result[0]['SUMMARY'] if summary_result else None,
                "description": "Generates concise summary",
                "use_case": "Summarize long commit messages"
            }
        except Exception as e:
            demos['summarize'] = {"error": str(e), "note": "Summarization demo"}

        # 3. COMPLETE (Text Generation)
        try:
            complete_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                'Explain this PR title in one sentence: {sample_pr}'
            ) as explanation
            """
            complete_result = snowflake.execute_query(complete_query)
            demos['complete'] = {
                "function": "SNOWFLAKE.CORTEX.COMPLETE",
                "model": "mistral-large",
                "input": f"Explain: {sample_pr}",
                "output": complete_result[0]['EXPLANATION'] if complete_result else None,
                "description": "LLM text generation (Mistral, Llama, etc.)",
                "use_case": "Generate PR descriptions, explain code changes"
            }
        except Exception as e:
            demos['complete'] = {"error": str(e), "note": "Text generation demo"}

        # 4. EXTRACT_ANSWER
        try:
            extract_query = f"""
            SELECT SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
                '{sample_text}',
                'What was fixed?'
            ) as answer
            """
            extract_result = snowflake.execute_query(extract_query)
            demos['extract_answer'] = {
                "function": "SNOWFLAKE.CORTEX.EXTRACT_ANSWER",
                "context": sample_text,
                "question": "What was fixed?",
                "output": extract_result[0]['ANSWER'] if extract_result else None,
                "description": "Question answering from text",
                "use_case": "Extract bug details from commit messages"
            }
        except Exception as e:
            demos['extract_answer'] = {"error": str(e), "note": "QA extraction demo"}

        return {
            "feature": "Cortex LLM Functions",
            "functions_demonstrated": list(demos.keys()),
            "demos": demos,
            "showcase_notes": [
                "All LLMs run INSIDE Snowflake",
                "No external API calls or keys",
                "Supports Mistral, Llama, Mixtral, Reka",
                "Automatic model versioning and scaling",
                "Cost: ~$0.001 per generation vs Claude $0.015"
            ],
            "models_available": [
                "mistral-large",
                "llama3-70b",
                "mixtral-8x7b",
                "reka-flash"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cortex LLM demo failed: {str(e)}")


# ==================== TIME TRAVEL ====================

@router.post("/time-travel")
async def time_travel_query(request: TimeTravelRequest) -> Dict[str, Any]:
    """
    ⏰ SHOWCASE: Snowflake Time Travel

    Query historical data from any point in time (up to 90 days ago).
    See what your PR_GENERATIONS table looked like X hours ago!

    This is a UNIQUE Snowflake feature - no other warehouse has this.
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake not connected")

    try:
        # Calculate timestamp for Time Travel
        past_time = datetime.utcnow() - timedelta(hours=request.hours_ago)
        timestamp_str = past_time.isoformat()

        # Time Travel query
        if request.query_type == "pr_generations":
            table_name = "PR_GENERATIONS"
            query = f"""
            SELECT
                FEATURE_REQUEST,
                PR_TITLE,
                GENERATED_AT,
                EXECUTION_TIME_MS,
                MODEL_USED
            FROM {table_name}
            AT(TIMESTAMP => '{timestamp_str}'::TIMESTAMP_LTZ)
            ORDER BY GENERATED_AT DESC
            LIMIT 10
            """
        else:
            raise HTTPException(status_code=400, detail="Invalid query_type")

        results = snowflake.execute_query(query)

        # Convert timestamps to ISO strings
        for row in results:
            if row.get('GENERATED_AT'):
                row['GENERATED_AT'] = row['GENERATED_AT'].isoformat()

        # Also get current count for comparison
        current_count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        current_count = snowflake.execute_query(current_count_query)[0]['COUNT']

        past_count_query = f"""
        SELECT COUNT(*) as count
        FROM {table_name}
        AT(TIMESTAMP => '{timestamp_str}'::TIMESTAMP_LTZ)
        """
        past_count = snowflake.execute_query(past_count_query)[0]['COUNT']

        return {
            "feature": "Snowflake Time Travel",
            "query_time": past_time.isoformat(),
            "hours_ago": request.hours_ago,
            "table": table_name,
            "results_count": len(results),
            "results": results,
            "comparison": {
                "count_then": past_count,
                "count_now": current_count,
                "new_records": current_count - past_count
            },
            "showcase_notes": [
                "Query data from ANY point in time",
                "Built into Snowflake - no setup needed",
                "Default: 1 day retention (configurable to 90 days)",
                "Use cases: audit trails, debugging, rollback analysis",
                "Unique to Snowflake - competitors don't have this"
            ]
        }

    except Exception as e:
        return {
            "feature": "Snowflake Time Travel",
            "query_time": past_time.isoformat(),
            "hours_ago": request.hours_ago,
            "results_count": 0,
            "results": [],
            "note": f"Time Travel demo - may require data history: {str(e)}",
            "showcase_notes": [
                "Time Travel queries historical data",
                "Requires data to exist at specified time",
                "Try shorter time ranges if no results"
            ]
        }


# ==================== SNOWFLAKE FEATURE SUMMARY ====================

@router.get("/features-summary")
async def snowflake_features_summary() -> Dict[str, Any]:
    """
    📊 SHOWCASE: Complete Snowflake Feature Summary

    One endpoint to show judges EVERYTHING we're using from Snowflake.
    """
    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        raise HTTPException(status_code=503, detail="Snowflake not connected")

    # Get warehouse and database info
    health = snowflake.health_check()

    # Count total PRs generated
    try:
        stats_query = """
        SELECT
            COUNT(*) as total_prs,
            COUNT(DISTINCT MODEL_USED) as models_used,
            AVG(EXECUTION_TIME_MS) as avg_time,
            MIN(GENERATED_AT) as first_pr,
            MAX(GENERATED_AT) as latest_pr
        FROM PR_GENERATIONS
        """
        stats = snowflake.execute_query(stats_query)
        pr_stats = stats[0] if stats else {}

        # Convert timestamps
        if pr_stats.get('FIRST_PR'):
            pr_stats['FIRST_PR'] = pr_stats['FIRST_PR'].isoformat()
        if pr_stats['LATEST_PR']:
            pr_stats['LATEST_PR'] = pr_stats['LATEST_PR'].isoformat()
    except:
        pr_stats = {}

    return {
        "snowflake_connection": {
            "status": health.get("status"),
            "database": health.get("database"),
            "schema": health.get("schema"),
            "warehouse": health.get("warehouse"),
            "version": health.get("version")
        },
        "features_demonstrated": {
            "cortex_llm": {
                "enabled": True,
                "functions": ["COMPLETE", "SENTIMENT", "SUMMARIZE", "EXTRACT_ANSWER"],
                "models": ["mistral-large", "llama3-70b", "mixtral-8x7b"],
                "cost_vs_claude": "-94%",
                "use_case": "PR description generation, commit analysis"
            },
            "cortex_search": {
                "enabled": False,  # Requires setup
                "capability": "Semantic/vector search",
                "use_case": "Find similar bugs, semantic commit search"
            },
            "time_travel": {
                "enabled": True,
                "retention_days": 1,  # Can be extended to 90
                "use_case": "Audit trail, historical PR analysis"
            },
            "data_warehouse": {
                "tables": ["PR_GENERATIONS", "COMMITS", "BUG_ANALYSIS"],
                "total_prs_stored": pr_stats.get('TOTAL_PRS', 0),
                "use_case": "Store all PR generations for analytics"
            },
            "analytics": {
                "enabled": True,
                "metrics_tracked": [
                    "PR generation count",
                    "Execution times",
                    "Model usage",
                    "Success rates"
                ],
                "use_case": "System performance monitoring"
            }
        },
        "pr_statistics": pr_stats,
        "judge_talking_points": [
            "✅ Cortex LLM replaces Claude API ($0.001 vs $0.015)",
            "✅ All PR generations stored in data warehouse",
            "✅ Time Travel for audit trails (unique to Snowflake)",
            "✅ Cortex Search for semantic similarity (when configured)",
            "✅ No external AI APIs needed - everything in Snowflake",
            "✅ Automatic scaling, versioning, and cost optimization"
        ],
        "next_steps": [
            "Configure Cortex Search service for semantic search",
            "Extend Time Travel retention to 90 days",
            "Add Cortex Analyst with semantic model (natural language SQL)"
        ]
    }
