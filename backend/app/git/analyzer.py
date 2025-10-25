"""Git repository analysis for commit extraction."""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from git import Repo
from git.objects import Commit

from app.config import config
from app.embeddings.client import embedding_client


class GitAnalyzer:
    """Analyzes git repositories and extracts commit data."""

    def __init__(self, repo_url: str):
        """Initialize git analyzer.

        Args:
            repo_url: GitHub repository URL
        """
        self.repo_url = repo_url
        self.repo_name = self._extract_repo_name(repo_url)
        self.repo: Optional[Repo] = None
        self.clone_path: Optional[Path] = None

    def _extract_repo_name(self, url: str) -> str:
        """Extract repository name from URL."""
        # Handle both SSH and HTTPS URLs
        # https://github.com/owner/repo.git -> owner/repo
        # git@github.com:owner/repo.git -> owner/repo
        parts = url.rstrip('/').rstrip('.git').split('/')
        return f"{parts[-2]}/{parts[-1]}"

    def clone_repo(self) -> Path:
        """Clone the repository to a temporary location.

        Returns:
            Path to cloned repository
        """
        # Create clone directory if it doesn't exist
        clone_base = Path(config.CLONE_DIR)
        clone_base.mkdir(parents=True, exist_ok=True)

        # Create unique directory for this repo
        repo_slug = self.repo_name.replace('/', '_')
        self.clone_path = clone_base / repo_slug

        # Remove existing clone if present
        if self.clone_path.exists():
            print(f"Removing existing clone at {self.clone_path}")
            shutil.rmtree(self.clone_path)

        # Clone repository
        print(f"Cloning {self.repo_url} to {self.clone_path}")
        self.repo = Repo.clone_from(self.repo_url, self.clone_path)
        print(f"Clone complete: {self.clone_path}")

        return self.clone_path

    def extract_commit_data(self, commit: Commit) -> Dict[str, Any]:
        """Extract structured data from a git commit.

        Args:
            commit: GitPython Commit object

        Returns:
            Dictionary matching Elasticsearch schema
        """
        # Get parent commits
        parent_shas = [parent.hexsha for parent in commit.parents]

        # Extract file changes
        files_changed = []
        total_additions = 0
        total_deletions = 0

        # Get diff from parent (or empty tree for first commit)
        if parent_shas:
            parent = commit.parents[0]
            diffs = parent.diff(commit, create_patch=True)
        else:
            # First commit - diff against empty tree
            diffs = commit.diff(None, create_patch=True)

        for diff in diffs:
            file_data = {
                'path': diff.b_path or diff.a_path,
                'change_type': diff.change_type,  # A, D, M, R
                'additions': 0,
                'deletions': 0,
                'diff': ''
            }

            # Count additions/deletions from diff
            if diff.diff:
                diff_text = diff.diff.decode('utf-8', errors='ignore')
                for line in diff_text.split('\n'):
                    if line.startswith('+') and not line.startswith('+++'):
                        file_data['additions'] += 1
                        total_additions += 1
                    elif line.startswith('-') and not line.startswith('---'):
                        file_data['deletions'] += 1
                        total_deletions += 1

                # Store diff (but schema has index: False to save space)
                file_data['diff'] = diff_text[:5000]  # Limit to 5KB per file

            files_changed.append(file_data)

        # Build commit document
        commit_data = {
            'sha': commit.hexsha,
            'author_name': commit.author.name,
            'author_email': commit.author.email,
            'committer_name': commit.committer.name,
            'committer_email': commit.committer.email,
            'commit_date': datetime.fromtimestamp(commit.committed_date).isoformat(),
            'message': commit.message.strip(),
            'repo_url': self.repo_url,
            'repo_name': self.repo_name,
            'files_changed': files_changed,
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'files_count': len(files_changed),
            'parent_shas': parent_shas
        }

        return commit_data

    def get_all_commits(
        self,
        max_commits: Optional[int] = None,
        generate_embeddings: bool = True
    ) -> List[Dict[str, Any]]:
        """Extract all commits from the repository.

        Args:
            max_commits: Optional limit on number of commits to extract
            generate_embeddings: Whether to generate embeddings for commit messages

        Returns:
            List of commit data dictionaries
        """
        if not self.repo:
            raise ValueError("Repository not cloned. Call clone_repo() first.")

        commits_data = []
        commit_iter = self.repo.iter_commits('--all')

        count = 0
        for commit in commit_iter:
            try:
                commit_data = self.extract_commit_data(commit)
                commits_data.append(commit_data)
                count += 1

                if count % 50 == 0:
                    print(f"Processed {count} commits...")

                if max_commits and count >= max_commits:
                    break

            except Exception as e:
                print(f"Error processing commit {commit.hexsha}: {e}")
                continue

        print(f"Extracted {len(commits_data)} commits")

        # Generate embeddings in batch for efficiency
        if generate_embeddings and commits_data:
            print("Generating embeddings for commit messages...")
            self._add_embeddings_batch(commits_data)

        return commits_data

    def _add_embeddings_batch(self, commits_data: List[Dict[str, Any]]):
        """Add embeddings to commit data in batches.

        Args:
            commits_data: List of commit dictionaries (modified in place)
        """
        # Extract all commit messages
        messages = [commit['message'] for commit in commits_data]

        # Generate embeddings in batch (100 at a time)
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            print(f"Embedding batch {i // batch_size + 1}/{(len(messages) + batch_size - 1) // batch_size}...")
            batch_embeddings = embedding_client.embed_batch(batch)
            all_embeddings.extend(batch_embeddings)

        # Add embeddings to commit data
        for commit, embedding in zip(commits_data, all_embeddings):
            commit['message_embedding'] = embedding

        print(f"✓ Generated {len(all_embeddings)} embeddings")

    def cleanup(self):
        """Remove cloned repository."""
        if self.clone_path and self.clone_path.exists():
            print(f"Cleaning up {self.clone_path}")
            shutil.rmtree(self.clone_path)
            self.clone_path = None
            self.repo = None
