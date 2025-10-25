# PM Copilot with Receipts

Transform vague PM specifications into actionable pull requests with full audit trails using Elasticsearch Serverless, Claude AI, and impact analysis.

## Overview

**PM speaks → Impact analysis → Code change → PR + receipts**

The system analyzes git commit history to understand code relationships, identifies impacted files through co-change detection, and generates minimal patches with full audit trails showing affected files, tests, and code owners.

## Features

- **Hybrid Search**: 3-way retrieval combining BM25 (lexical), kNN (semantic), and ELSER (learned sparse)
- **Impact Analysis**: Co-change detection using Jaccard similarity, code ownership tracking, test inference
- **Graph Exploration**: Visual co-change networks via Elasticsearch Graph API
- **MCP Integration**: Model Context Protocol server for Claude Desktop/Cursor
- **Agent Builder**: Registered tools for Elastic AI orchestration
- **GitHub Automation**: Automated PR creation with impact summaries

## Architecture

```
MCP Server (stdio)
    ↓
FastAPI Server (REST API)
    ↓
Elasticsearch Serverless
  ├── Commits Index (BM25 + kNN + ELSER)
  ├── Files Index (ownership, co-change, risk)
  └── Graph API (co-change networks)
```

## Tech Stack

- **Backend**: FastAPI 0.104.1, Python 3.10+
- **Search**: Elasticsearch 8.11.0 Serverless
- **Vector DB**: 1024-dim embeddings with int8_hnsw quantization
- **Git**: GitPython 3.1.40
- **GitHub**: PyGithub 2.1.1
- **MCP**: mcp 1.0.0

## Quick Start

### Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment

Create `backend/.env`:

```env
ELASTIC_API_KEY=your_elastic_api_key
ELASTIC_ENDPOINT=https://your-project.es.elastic-cloud.com
GITHUB_TOKEN=your_github_token
PORT=8000
CLONE_DIR=/tmp/bugrewind-clones
```

### Run FastAPI Server

```bash
cd backend
source venv/bin/activate
python app/main.py
```

Access API docs at `http://localhost:8000/docs`

### Run MCP Server (for Claude Desktop)

```bash
cd backend
source venv/bin/activate
python mcp_server.py
```

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "bugrewind": {
      "command": "python",
      "args": ["/path/to/backend/mcp_server.py"]
    }
  }
}
```

## API Endpoints

- **POST /api/search**: Hybrid search for commits (BM25 + kNN + ELSER)
- **POST /api/graph**: Explore co-change networks
- **POST /api/impact**: Get impact set for a file (owners, related files, risk)
- **POST /api/create-pr**: Create GitHub PR with patch
- **GET /health**: Health check

## MCP Tools

Three tools exposed via Model Context Protocol:

1. **impact.search**: Hybrid retrieval for relevant commits
2. **impact.graph**: Co-change network exploration
3. **impact.analyze**: File impact analysis (owners, related files, tests)

## Usage Example

```python
from app.git.analyzer import GitAnalyzer
from app.elastic.indexer import es_indexer
from app.elastic.files_indexer import files_indexer

# Clone and index repository
analyzer = GitAnalyzer("https://github.com/owner/repo")
analyzer.clone_repo()
commits = analyzer.get_all_commits(generate_embeddings=True)

# Index commits and build file metadata
es_indexer.bulk_index_commits(commits)
files_indexer.build_from_commits(commits, repo_id="owner/repo")

# Search for commits
from app.elastic.search import hybrid_searcher
from app.embeddings.client import embedding_client

query = "fix authentication bug"
query_vector = embedding_client.embed_text(query)
results = hybrid_searcher.hybrid_search(
    query_text=query,
    query_vector=query_vector,
    repo_id="owner/repo",
    size=10
)

# Get impact analysis
from app.elastic.files_indexer import files_indexer

impact = files_indexer.get_impact_set(
    file_path="src/auth/login.py",
    repo_id="owner/repo",
    min_co_change_score=0.3
)
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)**: Development guide and project context
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system architecture
- **[ELASTIC_PRIZE_README.md](ELASTIC_PRIZE_README.md)**: Elastic prize submission details

## Project Structure

```
backend/
├── app/
│   ├── analytics/          # Impact analysis (co-change, ownership)
│   ├── elastic/            # Elasticsearch integration
│   ├── embeddings/         # Vector generation
│   ├── git/                # Repository analysis
│   ├── github/             # GitHub PR automation
│   ├── config.py           # Configuration
│   └── main.py             # FastAPI server
├── mcp_server.py           # MCP stdio server
├── register_agent_builder_tools.py  # Agent Builder configs
├── test_mcp_client.py      # MCP testing
└── requirements.txt        # Dependencies
```

## License

MIT
