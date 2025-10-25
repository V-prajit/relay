"""Elasticsearch client for BugRewind."""
from elasticsearch import Elasticsearch
from app.config import config


class ElasticClient:
    """Wrapper for Elasticsearch client with connection management."""

    def __init__(self):
        """Initialize Elasticsearch client."""
        self._client = None

    def connect(self) -> Elasticsearch:
        """Connect to Elasticsearch serverless."""
        if self._client is None:
            self._client = Elasticsearch(
                config.ELASTIC_ENDPOINT,
                api_key=config.ELASTIC_API_KEY,
                request_timeout=config.ELASTIC_TIMEOUT
            )
        return self._client

    def get_client(self) -> Elasticsearch:
        """Get connected Elasticsearch client."""
        if self._client is None:
            return self.connect()
        return self._client

    def ping(self) -> bool:
        """Test Elasticsearch connection."""
        try:
            client = self.get_client()
            return client.ping()
        except Exception as e:
            print(f"Elasticsearch ping failed: {e}")
            return False

    def close(self):
        """Close Elasticsearch connection."""
        if self._client:
            self._client.close()
            self._client = None


# Global client instance
elastic_client = ElasticClient()
