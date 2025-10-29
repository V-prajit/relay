"""
GitHub service for creating pull requests and managing repository operations.

Uses PyGithub library to interact with GitHub API.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from github import Github, GithubException, Auth

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for GitHub operations like creating PRs and branches."""

    def __init__(self):
        """Initialize GitHub service with token from environment."""
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            logger.warning("GITHUB_TOKEN not found in environment variables")
            self.github = None
        else:
            # Use Auth class for authentication
            auth = Auth.Token(self.token)
            self.github = Github(auth=auth)
            logger.info("GitHub service initialized successfully")

    def _validate_initialized(self):
        """Check if GitHub client is initialized."""
        if not self.github:
            raise ValueError("GitHub service not initialized. GITHUB_TOKEN missing.")

    def _parse_repo_name(self, repo_url: str) -> str:
        """
        Extract owner/repo from GitHub URL.

        Args:
            repo_url: GitHub repository URL (https://github.com/owner/repo)

        Returns:
            Repository name in format "owner/repo"

        Example:
            "https://github.com/V-prajit/relay" → "V-prajit/relay"
        """
        # Remove trailing slash and .git if present
        clean_url = repo_url.rstrip('/').replace('.git', '')
        # Extract owner/repo from URL
        parts = clean_url.split('github.com/')[-1]
        return parts

    def create_pr(
        self,
        repo_url: str,
        title: str,
        description: str,
        branch_name: str,
        base_branch: str = "main",
        create_branch: bool = True
    ) -> Dict[str, Any]:
        """
        Create a GitHub pull request.

        Args:
            repo_url: GitHub repository URL
            title: PR title
            description: PR description/body
            branch_name: Name of the feature branch
            base_branch: Base branch to merge into (default: "main")
            create_branch: Whether to create the branch first (default: True)

        Returns:
            Dictionary with PR details:
                - success: bool
                - pr_url: str (PR URL)
                - pr_number: int
                - pr_title: str
                - branch_name: str
                - message: str (success/error message)

        Raises:
            ValueError: If GitHub service not initialized
            GithubException: If GitHub API call fails
        """
        self._validate_initialized()

        try:
            # Parse repository name
            repo_name = self._parse_repo_name(repo_url)
            logger.info(f"Creating PR for repository: {repo_name}")

            # Get repository object
            repo = self.github.get_repo(repo_name)

            # Get default branch if base_branch not found
            try:
                base_ref = repo.get_branch(base_branch)
                logger.info(f"Using base branch: {base_branch}")
            except GithubException:
                # Fall back to default branch
                base_branch = repo.default_branch
                base_ref = repo.get_branch(base_branch)
                logger.info(f"Base branch not found, using default: {base_branch}")

            # Create branch if requested
            if create_branch:
                try:
                    # Create new branch from base branch
                    repo.create_git_ref(
                        ref=f"refs/heads/{branch_name}",
                        sha=base_ref.commit.sha
                    )
                    logger.info(f"Created branch: {branch_name}")

                    # Create a placeholder commit so PR can be created
                    # This creates a README file with the PR description
                    try:
                        readme_path = f"PR_PROPOSAL_{branch_name.split('/')[-1]}.md"
                        repo.create_file(
                            path=readme_path,
                            message=f"docs: Add PR proposal for {title}",
                            content=f"# PR Proposal\n\n{description}\n\n---\n\nThis is a placeholder file. Actual code changes to be implemented.",
                            branch=branch_name
                        )
                        logger.info(f"Created placeholder commit on {branch_name}")
                    except Exception as e:
                        logger.warning(f"Could not create placeholder commit: {e}")

                except GithubException as e:
                    if "already exists" in str(e):
                        logger.warning(f"Branch {branch_name} already exists, using existing branch")
                    else:
                        raise

            # Create pull request
            pr = repo.create_pull(
                title=title,
                body=description,
                head=branch_name,
                base=base_branch
            )

            logger.info(f"Successfully created PR #{pr.number}: {pr.html_url}")

            return {
                "success": True,
                "pr_url": pr.html_url,
                "pr_number": pr.number,
                "pr_title": pr.title,
                "branch_name": branch_name,
                "base_branch": base_branch,
                "message": f"Pull request #{pr.number} created successfully"
            }

        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return {
                "success": False,
                "pr_url": None,
                "pr_number": None,
                "pr_title": title,
                "branch_name": branch_name,
                "message": f"GitHub API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error creating PR: {e}")
            return {
                "success": False,
                "pr_url": None,
                "pr_number": None,
                "pr_title": title,
                "branch_name": branch_name,
                "message": f"Error: {str(e)}"
            }

    def create_issue(
        self,
        repo_url: str,
        title: str,
        body: str,
        labels: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue.

        Args:
            repo_url: GitHub repository URL
            title: Issue title
            body: Issue body/description
            labels: Optional list of label names

        Returns:
            Dictionary with issue details
        """
        self._validate_initialized()

        try:
            repo_name = self._parse_repo_name(repo_url)
            repo = self.github.get_repo(repo_name)

            # Create issue
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )

            logger.info(f"Successfully created issue #{issue.number}: {issue.html_url}")

            return {
                "success": True,
                "issue_url": issue.html_url,
                "issue_number": issue.number,
                "message": f"Issue #{issue.number} created successfully"
            }

        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            return {
                "success": False,
                "issue_url": None,
                "issue_number": None,
                "message": f"Error: {str(e)}"
            }

    def get_repo_info(self, repo_url: str) -> Dict[str, Any]:
        """
        Get repository information.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Dictionary with repository details
        """
        self._validate_initialized()

        try:
            repo_name = self._parse_repo_name(repo_url)
            repo = self.github.get_repo(repo_name)

            return {
                "success": True,
                "name": repo.name,
                "full_name": repo.full_name,
                "default_branch": repo.default_branch,
                "description": repo.description,
                "url": repo.html_url
            }

        except Exception as e:
            logger.error(f"Error getting repo info: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }


# Singleton instance
github_service = GitHubService()
