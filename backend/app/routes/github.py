"""
GitHub API routes for creating pull requests and issues.

Endpoints:
- POST /api/github/create-pr - Create GitHub pull request
- POST /api/github/create-issue - Create GitHub issue
- GET /api/github/repo-info - Get repository information
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.services.github_service import github_service
from app.models.requests import CreatePRRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["GitHub"])


@router.post("/create-pr")
async def create_pull_request(request: CreatePRRequest) -> Dict[str, Any]:
    """
    Create a GitHub pull request.

    This endpoint creates a new branch and pull request on GitHub with the
    provided title and description.

    Args:
        request: CreatePRRequest with:
            - repo_url: GitHub repository URL
            - branch_name: Name for the feature branch
            - title: PR title
            - description: PR description
            - patch_content: (optional, not used for branch creation)

    Returns:
        Dictionary with PR details:
            - success: bool
            - pr_url: str (GitHub PR URL)
            - pr_number: int
            - pr_title: str
            - branch_name: str
            - message: str

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/github/create-pr \\
          -H "Content-Type: application/json" \\
          -d '{
            "repo_url": "https://github.com/V-prajit/relay",
            "branch_name": "feat/dark-mode-toggle",
            "title": "feat: Add dark mode toggle to settings",
            "description": "## Summary\\n- Adds dark mode toggle..."
          }'
        ```
    """
    try:
        logger.info(f"Creating PR for {request.repo_url} on branch {request.branch_name}")

        # Create PR using GitHub service
        result = github_service.create_pr(
            repo_url=request.repo_url,
            title=request.title,
            description=request.description,
            branch_name=request.branch_name,
            create_branch=True  # Always create branch
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating PR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pull request: {str(e)}"
        )


@router.post("/create-pr-from-generation")
async def create_pr_from_generation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create GitHub PR from Snowflake PR generation output.

    This endpoint takes the output from /api/snowflake/generate-pr
    and creates an actual GitHub pull request.

    Args:
        data: Dictionary with:
            - repo_url: GitHub repository URL
            - pr_title: Generated PR title
            - pr_description: Generated PR description
            - branch_name: Generated branch name

    Returns:
        Combined response with generation + GitHub PR details

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/snowflake/generate-pr \\
          -H "Content-Type: application/json" \\
          -d '{"feature_request":"Add dark mode","repo_name":"V-prajit/relay"}' \\
          | jq '{
              repo_url: "https://github.com/" + .repo_name,
              pr_title: .pr_title,
              pr_description: .pr_description,
              branch_name: .branch_name
            }' \\
          | curl -X POST http://localhost:8000/api/github/create-pr-from-generation \\
            -H "Content-Type: application/json" \\
            -d @-
        ```
    """
    try:
        # Extract required fields
        repo_url = data.get("repo_url")
        pr_title = data.get("pr_title")
        pr_description = data.get("pr_description")
        branch_name = data.get("branch_name")

        # Validate required fields
        if not all([repo_url, pr_title, pr_description, branch_name]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: repo_url, pr_title, pr_description, branch_name"
            )

        logger.info(f"Creating PR from generation for {repo_url}")

        # Create PR
        result = github_service.create_pr(
            repo_url=repo_url,
            title=pr_title,
            description=pr_description,
            branch_name=branch_name,
            create_branch=True
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        # Combine with original generation data
        return {
            **data,  # Include all original generation data
            "github_pr": result  # Add GitHub PR creation result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating PR from generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pull request: {str(e)}"
        )


@router.post("/create-issue")
async def create_issue(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a GitHub issue.

    Args:
        data: Dictionary with:
            - repo_url: GitHub repository URL
            - title: Issue title
            - body: Issue description
            - labels: Optional list of label names

    Returns:
        Dictionary with issue details

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/github/create-issue \\
          -H "Content-Type: application/json" \\
          -d '{
            "repo_url": "https://github.com/V-prajit/relay",
            "title": "Add dark mode toggle",
            "body": "We need a dark mode toggle in settings",
            "labels": ["enhancement", "ui"]
          }'
        ```
    """
    try:
        repo_url = data.get("repo_url")
        title = data.get("title")
        body = data.get("body")
        labels = data.get("labels", [])

        if not all([repo_url, title, body]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: repo_url, title, body"
            )

        result = github_service.create_issue(
            repo_url=repo_url,
            title=title,
            body=body,
            labels=labels
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create issue: {str(e)}"
        )


@router.get("/repo-info")
async def get_repo_info(repo_url: str) -> Dict[str, Any]:
    """
    Get GitHub repository information.

    Args:
        repo_url: GitHub repository URL

    Returns:
        Dictionary with repository details

    Example:
        ```bash
        curl "http://localhost:8000/api/github/repo-info?repo_url=https://github.com/V-prajit/relay"
        ```
    """
    try:
        result = github_service.get_repo_info(repo_url)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting repo info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get repository info: {str(e)}"
        )
