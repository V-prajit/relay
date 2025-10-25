"""Claude embedding client for generating vector representations of text."""
import httpx
from typing import List, Dict, Any
from app.config import config


class ClaudeEmbeddingClient:
    """Client for generating embeddings using Claude's embedding models."""

    def __init__(self):
        """Initialize the Claude embedding client."""
        self.api_key = config.CLAUDE_API_KEY
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-5-sonnet-20241022"  # Latest model with embeddings
        self.embedding_dim = 1024  # Claude embeddings are 1024-dimensional

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            1024-dimensional embedding vector
        """
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call (max 100 for efficiency)

        Returns:
            List of 1024-dimensional embedding vectors
        """
        if not texts:
            return []

        embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self._embed_batch_api(batch)
            embeddings.extend(batch_embeddings)

        return embeddings

    def _embed_batch_api(self, texts: List[str]) -> List[List[float]]:
        """Make API call to Claude for embedding generation.

        Note: As of 2025, Claude doesn't have a dedicated embedding endpoint.
        We simulate embeddings using the Messages API with a special prompt
        that extracts semantic features. For production, you'd use:
        - Voyage AI (recommended by Anthropic)
        - OpenAI text-embedding-3-large
        - Cohere embed-v3

        For this hackathon demo, we'll use a mock implementation that generates
        deterministic embeddings based on text hashing.
        """
        # MOCK IMPLEMENTATION for hackathon demo
        # In production, replace with actual embedding API call
        embeddings = []
        for text in texts:
            # Generate deterministic "embedding" from text hash
            # This is NOT a real embedding, just for demo purposes
            embedding = self._mock_embedding(text)
            embeddings.append(embedding)

        return embeddings

    def _mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding for demo purposes.

        In production, replace this with actual Claude/Voyage/OpenAI API call.

        Args:
            text: Input text

        Returns:
            1024-dimensional vector (mock)
        """
        import hashlib
        import math

        # Create deterministic hash
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()

        # Generate 1024 float values from hash
        embedding = []
        for i in range(1024):
            # Use hash bytes cyclically
            byte_idx = i % len(hash_bytes)
            # Convert to float in range [-1, 1]
            val = (hash_bytes[byte_idx] / 255.0) * 2 - 1
            # Add some variation based on position
            val = val * math.sin(i * 0.01)
            embedding.append(val)

        # Normalize to unit length (required for cosine similarity)
        magnitude = math.sqrt(sum(x * x for x in embedding))
        embedding = [x / magnitude for x in embedding]

        return embedding

    def embed_commit_message(self, message: str) -> List[float]:
        """Generate embedding specifically for commit messages.

        Args:
            message: Commit message text

        Returns:
            1024-dimensional embedding
        """
        # Preprocess commit message
        # Remove common prefixes, normalize whitespace
        cleaned = message.strip()
        cleaned = ' '.join(cleaned.split())  # Normalize whitespace

        return self.embed_text(cleaned)


# Global embedding client instance
embedding_client = ClaudeEmbeddingClient()


# Production-ready alternative using Voyage AI (recommended by Anthropic)
class VoyageEmbeddingClient:
    """Alternative embedding client using Voyage AI (production-ready).

    Voyage AI is recommended by Anthropic for production embeddings.
    See: https://docs.voyageai.com/
    """

    def __init__(self, api_key: str):
        """Initialize Voyage AI client."""
        self.api_key = api_key
        self.base_url = "https://api.voyageai.com/v1"
        self.model = "voyage-code-2"  # Optimized for code
        self.embedding_dim = 1024

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Voyage AI API."""
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "input": texts,
                    "model": self.model
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
