"""Commit indexing logic for Elasticsearch."""
from datetime import datetime
from typing import Dict, List, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from app.elastic.client import elastic_client
from app.elastic.schema import COMMIT_INDEX_MAPPING
from app.config import config


class CommitIndexer:
    """Handles indexing of git commits into Elasticsearch."""

    def __init__(self):
        """Initialize the commit indexer."""
        self.client: Elasticsearch = elastic_client.get_client()
        self.index_name = config.ELASTIC_INDEX_NAME

    def create_index(self, delete_if_exists: bool = False) -> bool:
        """Create the commits index with proper mapping.

        Args:
            delete_if_exists: If True, delete existing index before creating

        Returns:
            True if index was created, False if already exists
        """
        if delete_if_exists and self.client.indices.exists(index=self.index_name):
            print(f"Deleting existing index: {self.index_name}")
            self.client.indices.delete(index=self.index_name)

        if not self.client.indices.exists(index=self.index_name):
            print(f"Creating index: {self.index_name}")
            self.client.indices.create(
                index=self.index_name,
                body=COMMIT_INDEX_MAPPING
            )
            return True
        else:
            print(f"Index already exists: {self.index_name}")
            return False

    def index_commit(self, commit_data: Dict[str, Any]) -> bool:
        """Index a single commit.

        Args:
            commit_data: Commit data dictionary matching schema

        Returns:
            True if successful
        """
        try:
            # Add indexing timestamp
            commit_data['indexed_at'] = datetime.utcnow().isoformat()

            # Use commit SHA as document ID for deduplication
            doc_id = commit_data['sha']

            self.client.index(
                index=self.index_name,
                id=doc_id,
                document=commit_data
            )
            return True
        except Exception as e:
            print(f"Error indexing commit {commit_data.get('sha', 'unknown')}: {e}")
            return False

    def bulk_index_commits(self, commits: List[Dict[str, Any]], use_elser: bool = True) -> tuple[int, int]:
        """Bulk index multiple commits for better performance.

        Args:
            commits: List of commit data dictionaries
            use_elser: Whether to use ELSER inference pipeline for message_expansion

        Returns:
            Tuple of (success_count, error_count)
        """
        if not commits:
            return 0, 0

        # Prepare bulk actions
        actions = []
        for commit in commits:
            # Add indexing timestamp
            commit['indexed_at'] = datetime.utcnow().isoformat()

            # Prepare document for ELSER inference
            # Elasticsearch will automatically generate message_expansion via inference
            # if the ELSER model is deployed and the field is configured
            action = {
                '_index': self.index_name,
                '_id': commit['sha'],  # Use SHA as document ID
                '_source': commit
            }

            # If using inference pipeline for ELSER, specify it
            if use_elser:
                action['pipeline'] = 'elser-v2-pipeline'  # Optional: use ingest pipeline

            actions.append(action)

        # Execute bulk indexing
        try:
            success, errors = bulk(
                self.client,
                actions,
                raise_on_error=False,
                stats_only=False
            )
            error_count = len(errors) if isinstance(errors, list) else 0
            return success, error_count
        except Exception as e:
            print(f"Bulk indexing error: {e}")
            return 0, len(commits)

    def refresh_index(self):
        """Refresh the index to make recent changes searchable immediately."""
        self.client.indices.refresh(index=self.index_name)

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        try:
            stats = self.client.indices.stats(index=self.index_name)
            count = self.client.count(index=self.index_name)

            return {
                'document_count': count['count'],
                'size_bytes': stats['_all']['total']['store']['size_in_bytes'],
                'index_name': self.index_name
            }
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}


# Global indexer instance
commit_indexer = CommitIndexer()
