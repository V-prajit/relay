"""GitHub Pull Request creator for automated bug fixes."""
from typing import Dict, Any
from github import Github, GithubException
from app.config import config


class PRCreator:
    """Creates GitHub pull requests with bug fixes and analysis."""

    def __init__(self):
        """Initialize GitHub client."""
        if not config.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN not configured in environment")

        self.github = Github(config.GITHUB_TOKEN)

    def create_fix_pr(
        self,
        repo_url: str,
        branch_name: str,
        file_path: str,
        patch_content: str,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Create a GitHub PR with bug fix.

        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
            branch_name: New branch name for the fix
            file_path: Path to file being modified
            patch_content: New file content (full file, not diff)
            title: PR title
            description: PR description (markdown supported)

        Returns:
            Dict with pr_url, pr_number, branch
        """
        try:
            # Parse owner/repo from URL
            owner, repo_name = self._parse_repo_url(repo_url)

            # Get repository
            repo = self.github.get_repo(f"{owner}/{repo_name}")

            # Get default branch
            default_branch = repo.default_branch
            base_branch = repo.get_branch(default_branch)

            # Create new branch from default
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_branch.commit.sha
            )

            # Get file to update
            try:
                file_contents = repo.get_contents(file_path, ref=branch_name)
                # Update existing file
                repo.update_file(
                    path=file_path,
                    message=f"Fix: {title}",
                    content=patch_content,
                    sha=file_contents.sha,
                    branch=branch_name
                )
            except GithubException:
                # File doesn't exist, create it
                repo.create_file(
                    path=file_path,
                    message=f"Add: {title}",
                    content=patch_content,
                    branch=branch_name
                )

            # Create pull request
            pr = repo.create_pull(
                title=title,
                body=description,
                head=branch_name,
                base=default_branch
            )

            return {
                "pr_url": pr.html_url,
                "pr_number": pr.number,
                "branch": branch_name,
                "status": "created",
                "repo": f"{owner}/{repo_name}"
            }

        except GithubException as e:
            return {
                "status": "error",
                "error": str(e),
                "details": e.data if hasattr(e, 'data') else None
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Parse owner and repo name from GitHub URL.

        Args:
            repo_url: GitHub URL (https://github.com/owner/repo or git@github.com:owner/repo.git)

        Returns:
            Tuple of (owner, repo_name)
        """
        # Remove .git suffix
        url = repo_url.rstrip('/').rstrip('.git')

        # Handle HTTPS URLs
        if 'github.com/' in url:
            parts = url.split('github.com/')[-1].split('/')
            if len(parts) >= 2:
                return parts[0], parts[1]

        raise ValueError(f"Invalid GitHub URL: {repo_url}")


# Global instance
pr_creator = PRCreator() if config.GITHUB_TOKEN else None
