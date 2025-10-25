"""Configuration management for BugRewind backend."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration."""

    # Server
    PORT = int(os.getenv('PORT', '8000'))

    # APIs
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY', '')
    ELASTIC_ENDPOINT = os.getenv('ELASTIC_ENDPOINT', '')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')

    # Paths
    CLONE_DIR = os.getenv('CLONE_DIR', '/tmp/bugrewind-clones')

    # Elasticsearch
    ELASTIC_INDEX_NAME = 'commits'
    ELASTIC_TIMEOUT = 30

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration. Returns list of missing keys."""
        missing = []
        if not cls.ELASTIC_API_KEY:
            missing.append('ELASTIC_API_KEY')
        if not cls.ELASTIC_ENDPOINT:
            missing.append('ELASTIC_ENDPOINT')
        return missing


config = Config()
