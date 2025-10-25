"""Co-change analysis: find files that change together."""
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime, timedelta


class CoChangeAnalyzer:
    """Analyzes commit history to find files that frequently change together."""

    def __init__(self):
        """Initialize co-change analyzer."""
        self.file_pairs: Dict[Tuple[str, str], int] = defaultdict(int)
        self.file_commit_counts: Dict[str, int] = defaultdict(int)

    def analyze_commits(self, commits: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Analyze commits to compute co-change scores.

        Args:
            commits: List of commit dictionaries with files_changed

        Returns:
            Dict mapping file_path -> {other_file: co_change_score}
        """
        # Count co-occurrences
        for commit in commits:
            files = self._extract_file_paths(commit)

            # Count each file
            for file in files:
                self.file_commit_counts[file] += 1

            # Count pairs (order-independent)
            for i, file1 in enumerate(files):
                for file2 in files[i + 1:]:
                    pair = tuple(sorted([file1, file2]))
                    self.file_pairs[pair] += 1

        # Compute co-change scores
        co_change_scores = self._compute_scores()

        return co_change_scores

    def _extract_file_paths(self, commit: Dict[str, Any]) -> Set[str]:
        """Extract unique file paths from commit."""
        files_changed = commit.get('files_changed', [])

        if isinstance(files_changed, list) and files_changed:
            # Handle both nested structure and simple list
            if isinstance(files_changed[0], dict):
                return {f['path'] for f in files_changed}
            else:
                return set(files_changed)

        return set()

    def _compute_scores(self) -> Dict[str, Dict[str, float]]:
        """Compute co-change scores using Jaccard similarity.

        Score = co_occurrences / (commits_file1 + commits_file2 - co_occurrences)

        This gives a value between 0 and 1:
        - 1.0: Files always change together
        - 0.5: Files change together 50% of the time
        - 0.0: Files never change together
        """
        scores = defaultdict(dict)

        for (file1, file2), co_count in self.file_pairs.items():
            file1_count = self.file_commit_counts[file1]
            file2_count = self.file_commit_counts[file2]

            # Jaccard similarity
            score = co_count / (file1_count + file2_count - co_count)

            # Store bidirectionally
            scores[file1][file2] = round(score, 3)
            scores[file2][file1] = round(score, 3)

        return dict(scores)

    def get_top_related_files(
        self,
        file_path: str,
        co_change_scores: Dict[str, Dict[str, float]],
        min_score: float = 0.3,
        limit: int = 10
    ) -> List[Tuple[str, float]]:
        """Get files most likely to change with the given file.

        Args:
            file_path: File to find related files for
            co_change_scores: Pre-computed co-change scores
            min_score: Minimum score threshold
            limit: Maximum number of results

        Returns:
            List of (file_path, score) tuples, sorted by score descending
        """
        if file_path not in co_change_scores:
            return []

        related = co_change_scores[file_path]

        # Filter and sort
        results = [
            (path, score)
            for path, score in related.items()
            if score >= min_score
        ]
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]


def compute_file_ownership(commits: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Compute code ownership for each file.

    Args:
        commits: List of commit dictionaries

    Returns:
        Dict mapping file_path -> list of owners (sorted by contribution)
    """
    # Track contributions per file
    file_authors = defaultdict(lambda: defaultdict(lambda: {
        'commit_count': 0,
        'lines_changed': 0,
        'last_touched': None
    }))

    for commit in commits:
        author = commit.get('author_email', 'unknown')
        author_name = commit.get('author_name', 'Unknown')
        commit_date = commit.get('commit_date')

        files_changed = commit.get('files_changed', [])

        for file_info in files_changed:
            if isinstance(file_info, dict):
                file_path = file_info['path']
                additions = file_info.get('additions', 0)
                deletions = file_info.get('deletions', 0)
            else:
                continue

            # Update stats
            stats = file_authors[file_path][author]
            stats['commit_count'] += 1
            stats['lines_changed'] += additions + deletions
            stats['author_name'] = author_name

            # Update last touched date
            if commit_date:
                if isinstance(commit_date, str):
                    date = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                else:
                    date = commit_date

                if stats['last_touched'] is None or date > stats['last_touched']:
                    stats['last_touched'] = date

    # Convert to sorted lists (top-3 owners per file)
    ownership = {}
    for file_path, authors in file_authors.items():
        owners_list = []
        for author, stats in authors.items():
            owners_list.append({
                'author': author,
                'author_name': stats['author_name'],
                'commit_count': stats['commit_count'],
                'lines_changed': stats['lines_changed'],
                'last_touched': stats['last_touched'].isoformat() if stats['last_touched'] else None
            })

        # Sort by lines changed (primary) and commit count (secondary)
        owners_list.sort(
            key=lambda x: (x['lines_changed'], x['commit_count']),
            reverse=True
        )

        ownership[file_path] = owners_list[:3]  # Top-3 owners

    return ownership


def compute_recent_churn(
    commits: List[Dict[str, Any]],
    days: int = 30
) -> Dict[str, int]:
    """Compute recent churn (commit count in last N days) per file.

    Args:
        commits: List of commit dictionaries
        days: Number of days to look back

    Returns:
        Dict mapping file_path -> commit count in last N days
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    churn = defaultdict(int)

    for commit in commits:
        commit_date_str = commit.get('commit_date')
        if not commit_date_str:
            continue

        commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))

        if commit_date >= cutoff_date:
            files_changed = commit.get('files_changed', [])
            for file_info in files_changed:
                if isinstance(file_info, dict):
                    file_path = file_info['path']
                    churn[file_path] += 1

    return dict(churn)


# Global analyzer instance
co_change_analyzer = CoChangeAnalyzer()
