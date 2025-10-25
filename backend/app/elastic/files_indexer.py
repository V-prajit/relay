"""Files index management for impact analysis."""
from datetime import datetime
from typing import Dict, List, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from app.elastic.client import elastic_client
from app.elastic.schema import FILES_INDEX_MAPPING
from app.config import config
from app.analytics.co_change import (
    compute_file_ownership,
    compute_recent_churn,
    co_change_analyzer
)


class FilesIndexer:
    """Manages the files index for impact set analysis."""

    def __init__(self):
        """Initialize files indexer."""
        self.client: Elasticsearch = elastic_client.get_client()
        self.index_name = "files"  # Separate index for file metadata

    def create_index(self, delete_if_exists: bool = False) -> bool:
        """Create the files index.

        Args:
            delete_if_exists: Whether to delete existing index

        Returns:
            True if created
        """
        if delete_if_exists and self.client.indices.exists(index=self.index_name):
            print(f"Deleting existing index: {self.index_name}")
            self.client.indices.delete(index=self.index_name)

        if not self.client.indices.exists(index=self.index_name):
            print(f"Creating index: {self.index_name}")
            self.client.indices.create(
                index=self.index_name,
                body=FILES_INDEX_MAPPING
            )
            return True
        else:
            print(f"Index already exists: {self.index_name}")
            return False

    def build_from_commits(
        self,
        commits: List[Dict[str, Any]],
        repo_id: str
    ) -> int:
        """Build files index from commit data.

        Computes:
        - Code ownership (top-3 contributors)
        - Co-change scores
        - Recent churn
        - Test file relationships

        Args:
            commits: List of commit dictionaries
            repo_id: Repository identifier

        Returns:
            Number of files indexed
        """
        print(f"\nBuilding files index from {len(commits)} commits...")

        # Step 1: Compute ownership
        print("Computing code ownership...")
        ownership = compute_file_ownership(commits)

        # Step 2: Compute co-change scores
        print("Computing co-change scores...")
        co_change_scores = co_change_analyzer.analyze_commits(commits)

        # Step 3: Compute recent churn
        print("Computing recent churn (30 days)...")
        churn = compute_recent_churn(commits, days=30)

        # Step 4: Extract file metadata
        print("Extracting file metadata...")
        file_metadata = self._extract_file_metadata(commits)

        # Step 5: Build file documents
        print("Building file documents...")
        file_docs = []

        all_files = set(ownership.keys()) | set(co_change_scores.keys())

        for file_path in all_files:
            # Get metadata
            metadata = file_metadata.get(file_path, {})

            # Detect test files
            is_test = self._is_test_file(file_path)

            # Get file extension
            extension = '.' + file_path.split('.')[-1] if '.' in file_path else ''

            doc = {
                'file_path': file_path,
                'repo_id': repo_id,
                'extension': extension,
                'is_test_file': is_test,
                'owners': ownership.get(file_path, []),
                'co_change_scores': co_change_scores.get(file_path, {}),
                'recent_churn': churn.get(file_path, 0),
                'total_commits': metadata.get('total_commits', 0),
                'first_seen': metadata.get('first_seen'),
                'last_modified': metadata.get('last_modified'),
                'indexed_at': datetime.utcnow().isoformat()
            }

            # Find test relationships
            if is_test:
                doc['tests_for_files'] = self._infer_tested_files(file_path, all_files)
            else:
                doc['test_dependencies'] = self._find_test_files(file_path, all_files)

            file_docs.append(doc)

        # Step 6: Bulk index
        print(f"Indexing {len(file_docs)} files...")
        success_count = self.bulk_index_files(file_docs)

        print(f"✓ Indexed {success_count} files")
        return success_count

    def _extract_file_metadata(self, commits: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Extract first/last seen dates and commit counts per file."""
        metadata = {}

        for commit in commits:
            commit_date_str = commit.get('commit_date')
            if not commit_date_str:
                continue

            commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))

            files_changed = commit.get('files_changed', [])
            for file_info in files_changed:
                if isinstance(file_info, dict):
                    file_path = file_info['path']
                else:
                    continue

                if file_path not in metadata:
                    metadata[file_path] = {
                        'first_seen': commit_date,
                        'last_modified': commit_date,
                        'total_commits': 0
                    }

                # Update dates
                if commit_date < metadata[file_path]['first_seen']:
                    metadata[file_path]['first_seen'] = commit_date
                if commit_date > metadata[file_path]['last_modified']:
                    metadata[file_path]['last_modified'] = commit_date

                metadata[file_path]['total_commits'] += 1

        # Convert dates to ISO strings
        for file_path in metadata:
            metadata[file_path]['first_seen'] = metadata[file_path]['first_seen'].isoformat()
            metadata[file_path]['last_modified'] = metadata[file_path]['last_modified'].isoformat()

        return metadata

    def _is_test_file(self, file_path: str) -> bool:
        """Detect if a file is a test file."""
        test_indicators = [
            '/test/', '/tests/', '/__tests__/',
            '.test.', '.spec.',
            '_test.', '_spec.',
            'test_', 'spec_'
        ]

        file_lower = file_path.lower()
        return any(indicator in file_lower for indicator in test_indicators)

    def _infer_tested_files(self, test_file: str, all_files: set) -> List[str]:
        """Infer which files a test file tests (heuristic)."""
        # Simple heuristic: strip test suffix and look for matching file
        # e.g., src/auth/login.test.ts -> src/auth/login.ts

        tested = []

        # Remove test indicators
        base = test_file
        for indicator in ['.test.', '.spec.', '_test.', '_spec.']:
            base = base.replace(indicator, '.')

        # Remove test directory prefixes
        base = base.replace('/tests/', '/').replace('/test/', '/')

        # Look for matching files
        for file in all_files:
            if base == file or file.endswith(base):
                tested.append(file)

        return tested

    def _find_test_files(self, source_file: str, all_files: set) -> List[str]:
        """Find test files for a source file (inverse of _infer_tested_files)."""
        tests = []

        for file in all_files:
            if self._is_test_file(file):
                # Check if test file name relates to source file
                if source_file.split('/')[-1].split('.')[0] in file:
                    tests.append(file)

        return tests

    def bulk_index_files(self, files: List[Dict[str, Any]]) -> int:
        """Bulk index file documents.

        Args:
            files: List of file documents

        Returns:
            Number of files successfully indexed
        """
        if not files:
            return 0

        actions = []
        for file_doc in files:
            action = {
                '_index': self.index_name,
                '_id': f"{file_doc['repo_id']}:{file_doc['file_path']}",
                '_source': file_doc
            }
            actions.append(action)

        try:
            success, errors = bulk(
                self.client,
                actions,
                raise_on_error=False,
                stats_only=False
            )
            return success
        except Exception as e:
            print(f"Bulk indexing error: {e}")
            return 0

    def get_impact_set(
        self,
        file_path: str,
        repo_id: str,
        min_co_change_score: float = 0.3
    ) -> Dict[str, Any]:
        """Get impact set for a file (files that change with it).

        Args:
            file_path: File to get impact set for
            repo_id: Repository ID
            min_co_change_score: Minimum co-change score threshold

        Returns:
            Impact set with related files, owners, and metadata
        """
        doc_id = f"{repo_id}:{file_path}"

        try:
            result = self.client.get(
                index=self.index_name,
                id=doc_id
            )

            file_doc = result['_source']
            co_change_scores = file_doc.get('co_change_scores', {})

            # Filter by threshold
            related_files = [
                {'file': path, 'score': score}
                for path, score in co_change_scores.items()
                if score >= min_co_change_score
            ]

            # Sort by score
            related_files.sort(key=lambda x: x['score'], reverse=True)

            return {
                'file_path': file_path,
                'owners': file_doc.get('owners', []),
                'related_files': related_files,
                'test_dependencies': file_doc.get('test_dependencies', []),
                'recent_churn': file_doc.get('recent_churn', 0)
            }

        except Exception as e:
            print(f"Error retrieving impact set: {e}")
            return {}

    def refresh_index(self):
        """Refresh the index."""
        self.client.indices.refresh(index=self.index_name)


# Global files indexer instance
files_indexer = FilesIndexer()
