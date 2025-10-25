"""
Response models for BugRewind API.

Contains all Pydantic models for API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CommitInfo(BaseModel):
    """
    Information about a single commit.

    Used in commit history responses.
    """

    commit_hash: str = Field(
        ...,
        description="Git commit hash (SHA-1)",
        examples=["a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"]
    )
    author: str = Field(
        ...,
        description="Commit author name",
        examples=["John Doe"]
    )
    timestamp: int = Field(
        ...,
        description="Unix timestamp of commit",
        examples=[1698765432]
    )
    message: str = Field(
        ...,
        description="Commit message",
        examples=["Fix authentication logic"]
    )
    line_number: Optional[int] = Field(
        None,
        description="Line number this commit affected (if applicable)",
        examples=[45]
    )


class ClaudeAnalysis(BaseModel):
    """
    AI analysis results from Claude.

    Contains root cause analysis and suggested fixes.
    """

    root_cause: str = Field(
        ...,
        description="Explanation of why this change caused the bug",
        examples=["The commit removed a null check before accessing user.email, causing a TypeError when user is undefined"]
    )
    developer_intent: str = Field(
        ...,
        description="What the developer was trying to accomplish",
        examples=["Simplify the authentication flow by removing redundant checks"]
    )
    minimal_patch: str = Field(
        ...,
        description="Suggested fix in unified diff format",
        examples=["diff --git a/auth.py b/auth.py\n@@ -45,1 +45,3 @@\n+if user is None:\n+    return None\nreturn user.email"]
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence level of the analysis (0.0 to 1.0)",
        examples=[0.85]
    )


class AnalyzeBugResponse(BaseModel):
    """
    Response from bug analysis endpoint.

    Contains the suspect commit, history, and AI analysis.
    """

    first_bad_commit: str = Field(
        ...,
        description="Hash of the commit that likely introduced the bug",
        examples=["a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"]
    )
    commits: List[CommitInfo] = Field(
        ...,
        description="List of commits that touched the affected code",
        examples=[[]]
    )
    file_path: str = Field(
        ...,
        description="Path to the file that was analyzed",
        examples=["src/auth/login.py"]
    )
    analysis: ClaudeAnalysis = Field(
        ...,
        description="AI-powered root cause analysis"
    )


class CreatePRResponse(BaseModel):
    """
    Response from pull request creation endpoint.

    Contains PR URL and status.
    """

    success: bool = Field(
        ...,
        description="Whether the PR was created successfully",
        examples=[True]
    )
    pr_url: str = Field(
        ...,
        description="URL of the created pull request",
        examples=["https://github.com/user/repo/pull/123"]
    )
    branch_name: str = Field(
        ...,
        description="Name of the branch that was created",
        examples=["fix/auth-401-error"]
    )


class ErrorResponse(BaseModel):
    """
    Structured error response.

    Provides actionable error information to the client.
    """

    error: str = Field(
        ...,
        description="Human-readable error message explaining what went wrong",
        examples=["File 'auth.py' not found in repository"]
    )
    suggestion: str = Field(
        ...,
        description="Actionable suggestion for how to fix the error",
        examples=["Check the file path - try 'src/auth.py' or use OCR to auto-detect"]
    )
    status: int = Field(
        ...,
        description="HTTP status code",
        examples=[404]
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional technical details (only in debug mode)",
        examples=[{"traceback": "..."}]
    )
