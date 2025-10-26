"""
Request models for BugRewind API.

Contains all Pydantic models for incoming API requests.
"""

from typing import Annotated, Optional
from pydantic import BaseModel, Field, AfterValidator, field_validator


def validate_github_url(v: str) -> str:
    """Validate that the URL is a GitHub URL."""
    if not v.startswith("https://github.com"):
        raise ValueError("Repository URL must be a GitHub URL starting with https://github.com")
    return v


def validate_non_empty(v: str) -> str:
    """Validate that a string is not empty after stripping whitespace."""
    if not v.strip():
        raise ValueError("Value cannot be empty")
    return v.strip()


# Create reusable custom types
GitHubURL = Annotated[str, AfterValidator(validate_github_url)]
NonEmptyStr = Annotated[str, AfterValidator(validate_non_empty)]


class AnalyzeBugRequest(BaseModel):
    """
    Request model for analyzing a bug in a repository.

    Used by POST /api/analyze-bug endpoint.
    """

    repo_url: GitHubURL = Field(
        ...,
        description="GitHub repository URL",
        examples=["https://github.com/user/repo"]
    )
    bug_description: str = Field(
        ...,
        min_length=10,
        description="Description of the bug to analyze",
        examples=["Authentication fails with 401 error when using valid credentials"]
    )
    file_path: NonEmptyStr = Field(
        ...,
        description="Path to the file containing the bug",
        examples=["src/auth/login.py"]
    )
    line_hint: Optional[int] = Field(
        None,
        ge=1,
        description="Optional line number hint where the bug might be located",
        examples=[45]
    )


class CreatePRRequest(BaseModel):
    """
    Request model for creating a pull request with a bug fix.

    Used by POST /api/create-pr endpoint.
    """

    repo_url: GitHubURL = Field(
        ...,
        description="GitHub repository URL",
        examples=["https://github.com/user/repo"]
    )
    branch_name: NonEmptyStr = Field(
        ...,
        description="Name for the new branch",
        examples=["fix/auth-401-error"]
    )
    patch_content: str = Field(
        ...,
        min_length=1,
        description="Unified diff patch content",
        examples=["diff --git a/auth.py b/auth.py\n..."]
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Pull request title",
        examples=["Fix: Resolve authentication 401 error"]
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Pull request description with analysis",
        examples=["This PR fixes the authentication bug by adding proper null checks..."]
    )


class OCRAnalyzeRequest(BaseModel):
    """
    Request model for analyzing a bug from a screenshot using OCR.

    Used by POST /api/analyze-bug-from-image endpoint.
    """

    image_data: NonEmptyStr = Field(
        ...,
        description="Base64 encoded image data",
        examples=["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="]
    )
    bug_description: str = Field(
        ...,
        min_length=10,
        description="Description of what you're seeing in the error",
        examples=["Got this error in terminal and don't know where it's from"]
    )
    repo_url: GitHubURL = Field(
        ...,
        description="GitHub repository URL to analyze",
        examples=["https://github.com/user/repo"]
    )


class GeneratePRRequest(BaseModel):
    """
    Request model for generating PR content using Snowflake Cortex LLM.

    Used by POST /api/snowflake/generate-pr endpoint.
    This is called by Postman AI Agent as a tool.
    """

    feature_request: str = Field(
        ...,
        min_length=5,
        description="The feature request from PM (natural language)",
        examples=["fix mobile login responsive design", "add OAuth authentication"]
    )
    impacted_files: list[str] = Field(
        default_factory=list,
        description="List of files that will be modified (from Ripgrep search)",
        examples=[["src/pages/Login.tsx", "src/components/Header.tsx"]]
    )
    is_new_feature: bool = Field(
        default=False,
        description="Whether this is a new feature (no existing files found)",
        examples=[False]
    )
    repo_name: str = Field(
        ...,
        min_length=1,
        description="Repository name (owner/repo format)",
        examples=["V-prajit/youareabsolutelyright"]
    )
    conflict_info: Optional[str] = Field(
        None,
        description="Optional conflict information from PR analysis",
        examples=["Conflicts with PR #42 (Settings.tsx overlap)"]
    )
