# Elasticsearch Serverless Setup Guide

## Step 1: Create Elasticsearch Serverless Account

### 1.1 Sign Up for Elastic Cloud

1. Go to **https://cloud.elastic.co/**
2. Click **"Start free trial"**
3. Choose sign-up method:
   - **Google** (recommended - fastest)
   - **Microsoft**
   - **Email** (requires verification)

4. **Trial includes**:
   - 14 days free
   - No credit card required
   - Full serverless features
   - ELSER model access

### 1.2 Create Serverless Project

1. After login, click **"Create project"**
2. **Project type**: Select **"Serverless"** (not "Elasticsearch")
3. **Project name**: `bugrewind` (or any name)
4. **Region**: Choose closest to you:
   - `us-east-1` (Virginia)
   - `us-west-2` (Oregon)
   - `eu-west-1` (Ireland)
   - `ap-southeast-1` (Singapore)

5. Click **"Create project"**
6. Wait ~2-3 minutes for provisioning

### 1.3 Get API Credentials

After project is created:

1. Click **"Manage this project"**
2. Go to **"Project settings"** (gear icon)
3. Click **"Management" → "API keys"**
4. Click **"Create API key"**
5. **Name**: `bugrewind-backend`
6. **Permissions**: Select **"All"** (or custom with read/write)
7. Click **"Create API key"**
8. **IMPORTANT**: Copy the key immediately (shown only once)
   ```
   Format: dXNlcjp...base64...string
   ```

9. Save to `backend/.env`:
   ```env
   ELASTIC_API_KEY=dXNlcjpwYXNzd29yZA==
   ```

### 1.4 Get Elasticsearch Endpoint

1. In project overview, find **"Copy endpoint"** button
2. Format: `https://your-project-id.es.us-east-1.aws.elastic.cloud:443`
3. Save to `backend/.env`:
   ```env
   ELASTIC_ENDPOINT=https://your-project-id.es.us-east-1.aws.elastic.cloud:443
   ```

## Step 2: Deploy ELSER Model (For Hybrid Search)

ELSER (Elastic Learned Sparse EncodeR) is required for 3-way hybrid search.

### 2.1 Via Kibana Console

1. In Elastic Cloud dashboard, click **"Open Kibana"**
2. In left sidebar, go to **"Dev Tools" → "Console"**
3. Run this command:

```json
POST _ml/trained_models/.elser_model_2_linux-x86_64/_deploy
{
  "number_of_allocations": 1,
  "threads_per_allocation": 1
}
```

4. **Expected response**:
```json
{
  "assignment": {
    "task_parameters": {
      "model_id": ".elser_model_2_linux-x86_64",
      "deployment_id": ".elser_model_2_linux-x86_64"
    },
    "routing_table": { ... },
    "assignment_state": "started"
  }
}
```

5. **Wait 2-5 minutes** for deployment
6. Verify deployment:
```json
GET _ml/trained_models/.elser_model_2_linux-x86_64/_stats
```

Should show `"deployment_state": "started"`

### 2.2 Alternative: Via Python

```python
from app.elastic.client import elastic_client

# Deploy ELSER
elastic_client.ml.start_trained_model_deployment(
    model_id=".elser_model_2_linux-x86_64",
    number_of_allocations=1,
    threads_per_allocation=1
)
```

## Step 3: Configure Backend Environment

### 3.1 Create .env File

```bash
cd backend
cp .env.example .env  # If .env.example exists, else create new
```

### 3.2 Fill in Variables

```env
# Elasticsearch Serverless (REQUIRED)
ELASTIC_API_KEY=dXNlcjpwYXNzd29yZA==  # From Step 1.3
ELASTIC_ENDPOINT=https://your-project.es.us-east-1.aws.elastic.cloud:443  # From Step 1.4

# GitHub (OPTIONAL - for PR creation)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx  # Get from https://github.com/settings/tokens

# Server Config
PORT=8000
CLONE_DIR=/tmp/bugrewind-clones

# Embedding (Optional - currently using mock)
# VOYAGE_API_KEY=xxxxx  # For production embeddings
```

### 3.3 Get GitHub Token (Optional)

1. Go to **https://github.com/settings/tokens**
2. Click **"Generate new token (classic)"**
3. **Scopes**: Select:
   - `repo` (full control)
   - `workflow` (if using Actions)
4. Click **"Generate token"**
5. Copy token (starts with `ghp_`)
6. Add to `.env`

## Step 4: Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Verify installation**:
```bash
python -c "import elasticsearch; print(elasticsearch.__version__)"
# Should print: 8.11.0 or similar
```

## Step 5: Test Elasticsearch Connection

### 5.1 Create Test Script

Create `backend/test_elastic.py`:

```python
from app.config import config
from app.elastic.client import elastic_client

def test_connection():
    """Test Elasticsearch connection."""
    print("Testing Elasticsearch connection...")
    print(f"Endpoint: {config.ELASTIC_ENDPOINT}")

    try:
        # Ping server
        if elastic_client.ping():
            print("✓ Connection successful!")
        else:
            print("✗ Connection failed (ping returned False)")
            return False

        # Get cluster info
        info = elastic_client.info()
        print(f"✓ Cluster name: {info['cluster_name']}")
        print(f"✓ Elasticsearch version: {info['version']['number']}")

        # Check ELSER model
        try:
            stats = elastic_client.ml.get_trained_models_stats(
                model_id=".elser_model_2_linux-x86_64"
            )
            deployment_state = stats['trained_model_stats'][0]['deployment_stats']['state']
            print(f"✓ ELSER model state: {deployment_state}")

            if deployment_state != "started":
                print("⚠ ELSER model not started. Run: POST _ml/trained_models/.elser_model_2_linux-x86_64/_deploy")
        except Exception as e:
            print(f"⚠ ELSER model not found: {e}")
            print("  Deploy it with: POST _ml/trained_models/.elser_model_2_linux-x86_64/_deploy")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

### 5.2 Run Test

```bash
cd backend
source venv/bin/activate
python test_elastic.py
```

**Expected output**:
```
Testing Elasticsearch connection...
Endpoint: https://your-project.es...
✓ Connection successful!
✓ Cluster name: your-project-id
✓ Elasticsearch version: 8.15.0
✓ ELSER model state: started
```

## Step 6: Create Indices

### 6.1 Create Commits Index

Create `backend/setup_indices.py`:

```python
from app.elastic.client import elastic_client
from app.elastic.schema import COMMITS_INDEX_CONFIG, FILES_INDEX_CONFIG

def create_indices():
    """Create Elasticsearch indices."""

    # Create commits index
    commits_index = "commits"
    if not elastic_client.indices.exists(index=commits_index):
        print(f"Creating {commits_index} index...")
        elastic_client.indices.create(
            index=commits_index,
            body=COMMITS_INDEX_CONFIG
        )
        print(f"✓ {commits_index} index created")
    else:
        print(f"✓ {commits_index} index already exists")

    # Create files index
    files_index = "files"
    if not elastic_client.indices.exists(index=files_index):
        print(f"Creating {files_index} index...")
        elastic_client.indices.create(
            index=files_index,
            body=FILES_INDEX_CONFIG
        )
        print(f"✓ {files_index} index created")
    else:
        print(f"✓ {files_index} index already exists")

    print("\nAll indices ready!")

if __name__ == "__main__":
    create_indices()
```

### 6.2 Run Setup

```bash
python setup_indices.py
```

**Expected output**:
```
Creating commits index...
✓ commits index created
Creating files index...
✓ files index created

All indices ready!
```

## Step 7: Index Sample Repository

### 7.1 Create Indexing Script

Create `backend/index_repo.py`:

```python
import sys
from app.git.analyzer import GitAnalyzer
from app.elastic.indexer import es_indexer
from app.elastic.files_indexer import files_indexer

def index_repository(repo_url, max_commits=50):
    """Index a git repository."""

    print(f"Indexing repository: {repo_url}")
    print(f"Max commits: {max_commits}")

    # Clone and analyze
    analyzer = GitAnalyzer(repo_url)
    try:
        analyzer.clone_repo()
        commits = analyzer.get_all_commits(
            max_commits=max_commits,
            generate_embeddings=True
        )

        print(f"\n✓ Extracted {len(commits)} commits")

        # Index commits
        print("\nIndexing commits...")
        es_indexer.bulk_index_commits(commits)
        print("✓ Commits indexed")

        # Build file metadata
        print("\nBuilding file metadata...")
        files_indexer.build_from_commits(
            commits,
            repo_id=analyzer.repo_name
        )
        print("✓ File metadata indexed")

        print(f"\n✅ Successfully indexed {repo_url}")

    finally:
        analyzer.cleanup()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python index_repo.py <repo_url> [max_commits]")
        print("Example: python index_repo.py https://github.com/facebook/react 50")
        sys.exit(1)

    repo_url = sys.argv[1]
    max_commits = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    index_repository(repo_url, max_commits)
```

### 7.2 Index a Test Repo

```bash
# Small repo for testing
python index_repo.py https://github.com/tj/commander.js 50

# Or your own repo
python index_repo.py https://github.com/your-username/your-repo 50
```

**Expected output**:
```
Indexing repository: https://github.com/tj/commander.js
Max commits: 50
Cloning...
Clone complete
Processed 50 commits...
Extracted 50 commits
Generating embeddings for commit messages...
Embedding batch 1/1...
✓ Generated 50 embeddings

Indexing commits...
Indexed 50 commits
✓ Commits indexed

Building file metadata...
✓ File metadata indexed

✅ Successfully indexed https://github.com/tj/commander.js
```

## Step 8: Test Hybrid Search

### 8.1 Create Search Test

Create `backend/test_search.py`:

```python
from app.elastic.search import hybrid_searcher
from app.embeddings.client import embedding_client

def test_search():
    """Test hybrid search."""

    query = "fix bug"
    print(f"Searching for: '{query}'")

    # Generate query vector
    query_vector = embedding_client.embed_text(query)
    print(f"✓ Query vector generated ({len(query_vector)} dimensions)")

    # Hybrid search
    results = hybrid_searcher.hybrid_search(
        query_text=query,
        query_vector=query_vector,
        size=5
    )

    print(f"\n✓ Found {results['hits']['total']['value']} results")
    print("\nTop 5 commits:")

    for i, hit in enumerate(results['hits']['hits'][:5], 1):
        fields = hit.get('fields', {})
        sha = fields.get('sha', ['unknown'])[0][:8]
        message = fields.get('message', [''])[0][:60]
        score = hit.get('_score', 0)

        print(f"{i}. [{sha}] {message}... (score: {score:.2f})")

    # Test aggregations
    aggs = results.get('aggregations', {})
    if 'impacted_files' in aggs:
        print("\nTop impacted files:")
        for bucket in aggs['impacted_files']['file_paths']['buckets'][:3]:
            print(f"  - {bucket['key']} ({bucket['doc_count']} commits)")

if __name__ == "__main__":
    test_search()
```

### 8.2 Run Search Test

```bash
python test_search.py
```

**Expected output**:
```
Searching for: 'fix bug'
✓ Query vector generated (1024 dimensions)

✓ Found 23 results

Top 5 commits:
1. [a1b2c3d4] Fix: Handle null values in parser... (score: 12.45)
2. [e5f6g7h8] Fix bug with option parsing... (score: 11.23)
3. [i9j0k1l2] Bugfix: Correct version handling... (score: 10.87)
4. [m3n4o5p6] Fix regression in help text... (score: 9.56)
5. [q7r8s9t0] Fix: Update dependencies... (score: 8.34)

Top impacted files:
  - lib/command.js (15 commits)
  - test/test.js (12 commits)
  - README.md (8 commits)
```

## Step 9: Start FastAPI Server

```bash
cd backend
source venv/bin/activate
python app/main.py
```

**Expected output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 9.1 Test Endpoints

Open browser: **http://localhost:8000/docs**

You should see **Swagger UI** with 5 endpoints:
- `GET /health`
- `POST /api/search`
- `POST /api/graph`
- `POST /api/impact`
- `POST /api/create-pr`

### 9.2 Test Health Endpoint

```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{
  "status": "ok",
  "elastic_connected": true,
  "elastic_endpoint": "https://your-project.es...",
  "version": "1.0.0"
}
```

### 9.3 Test Search Endpoint

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fix bug",
    "size": 5
  }'
```

## Step 10: Start MCP Server

```bash
# In another terminal
cd backend
source venv/bin/activate
python mcp_server.py
```

**Expected output**:
```
MCP server running on stdio
Ready to receive requests...
```

### 10.1 Test MCP Server

```bash
# In another terminal
python test_mcp_client.py
```

## Troubleshooting

### Issue: "Connection refused"
**Cause**: Wrong endpoint or API key
**Fix**:
1. Verify endpoint in Elastic Cloud console
2. Regenerate API key if needed
3. Check firewall/VPN settings

### Issue: "ELSER model not found"
**Cause**: Model not deployed
**Fix**: Run Step 2 (Deploy ELSER)

### Issue: "SSL certificate verify failed"
**Cause**: Python SSL issues
**Fix**:
```bash
pip install --upgrade certifi
```

### Issue: "Index not found"
**Cause**: Indices not created
**Fix**: Run Step 6 (Create Indices)

### Issue: "Out of memory"
**Cause**: Too many commits at once
**Fix**: Use smaller `max_commits` (e.g., 50 instead of 1000)

## What to Add to Backend (Optional Enhancements)

### 1. Real Embeddings (Instead of Mock)

**Option A: Voyage AI** (Recommended)
```bash
pip install voyageai
```

```python
# app/embeddings/client.py
from voyageai import Client as VoyageClient

class VoyageEmbeddingClient:
    def __init__(self):
        self.client = VoyageClient(api_key=config.VOYAGE_API_KEY)

    def embed_text(self, text):
        result = self.client.embed([text], model="voyage-2")
        return result.embeddings[0]
```

**Option B: OpenAI**
```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(api_key=config.OPENAI_API_KEY)
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)
return response.data[0].embedding
```

### 2. Webhook for Automatic Indexing

Add webhook endpoint that indexes commits on push:

```python
# app/main.py
@app.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub push webhook."""
    payload = await request.json()

    if payload.get('ref') == 'refs/heads/main':
        repo_url = payload['repository']['clone_url']
        # Index new commits
        ...
```

### 3. Incremental Indexing

Track last indexed commit and only index new ones:

```python
def incremental_index(repo_url):
    """Index only new commits since last run."""
    last_sha = get_last_indexed_sha(repo_url)
    new_commits = get_commits_since(repo_url, last_sha)
    index_commits(new_commits)
```

### 4. Search Filters

Add filters to search endpoint:
- Date range
- Author
- File type
- Commit size

### 5. Caching

Add Redis for caching search results:

```bash
pip install redis
```

```python
@app.post("/api/search")
async def search_commits(request: SearchRequest):
    cache_key = f"search:{request.query}:{request.size}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    results = hybrid_searcher.hybrid_search(...)
    redis.setex(cache_key, 300, json.dumps(results))  # 5min cache
    return results
```

## Next Steps

1. ✅ **Elasticsearch configured** - You now have API key and endpoint
2. ✅ **Indices created** - commits and files indices ready
3. ✅ **ELSER deployed** - 3-way hybrid search working
4. ✅ **Sample repo indexed** - Test data available
5. ✅ **FastAPI running** - REST endpoints accessible
6. ✅ **MCP server running** - Tools exposed

**Ready to build frontend!** 🎉

See `FRONTEND_MCP_PLAN.md` for Phase 1-6 implementation.
