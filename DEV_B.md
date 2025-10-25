# DEV_B_GUIDE.md

```markdown
# DEV B: Elastic Serverless + Postman Flows

**Your Mission:** Set up Elastic Serverless for commit indexing, build Postman Flow with AI Agent orchestration, deploy as public Action

**Time Budget:** 22 hours total
- Hours 0-4: Elastic setup + data ingestion
- Hours 4-8: Search queries + testing
- Hours 8-14: Postman Flow creation
- Hours 14-18: Deploy as Action + integration
- Hours 18-22: Testing + documentation

---

## Hour 0-2: Elastic Serverless Setup

### Step 1: Create Elastic Account & Project

**Manual steps (browser):**

1. Go to https://cloud.elastic.co
2. Click "Start free trial" or "Sign up"
3. Use your @uta.edu email (might get edu credits)
4. Verify email
5. After login, click "Create deployment"
6. **Important:** Choose "Serverless" (not Elasticsearch)
   - Project name: `bugrewind`
   - Region: `us-central1` (or closest to you)
   - Click "Create project"

7. **SAVE THESE IMMEDIATELY:**
   - API Key (shows once - copy it!)
   - Endpoint URL (looks like: `https://bugrewind-abc123.es.us-central1.gcp.cloud.es.io`)
   - Project ID

8. Add to backend/.env:
   ```env
   ELASTIC_API_KEY=your_key_here
   ELASTIC_ENDPOINT=your_endpoint_here
   ```

**Expected result:** Working Elastic Serverless project

---

### Step 2: Test Connection

**Create backend/scripts/test_elastic.py:**

**Prompt for Claude Code:**
```
Create a Python script that tests Elastic connection:

1. Import:
   - elasticsearch (Elasticsearch client)
   - os
   - dotenv (load_dotenv)
   - json

2. Load environment variables

3. Create Elasticsearch client:
   from elasticsearch import Elasticsearch
   
   client = Elasticsearch(
       cloud_id=None,  # Not needed for serverless
       api_key=os.getenv("ELASTIC_API_KEY"),
       hosts=[os.getenv("ELASTIC_ENDPOINT")]
   )

4. Test connection:
   - Try client.info()
   - Print cluster info
   - Print "✓ Connected successfully!"

5. Error handling:
   - Connection errors
   - Authentication errors
   - Print helpful error messages

Make it executable: python scripts/test_elastic.py
```

**Run it:**
```bash
cd backend
python scripts/test_elastic.py
```

**Expected output:**
```
✓ Connected to Elastic Serverless
Cluster: bugrewind
Version: 9.2.0
✓ Connection successful!
```

---

### Step 3: Create Elastic Service Module

**Prompt for Claude Code:**
```
Create backend/app/services/elastic_service.py:

Purpose: Handle all Elastic operations for commit indexing and searching

1. Import:
   - elasticsearch (Elasticsearch, helpers)
   - os
   - typing (List, Dict, Optional, Any)
   - datetime
   - logging

2. Class: ElasticService

   __init__(self):
   - Create Elasticsearch client:
     self.client = Elasticsearch(
         hosts=[os.getenv("ELASTIC_ENDPOINT")],
         api_key=os.getenv("ELASTIC_API_KEY"),
         request_timeout=30,
         max_retries=3,
         retry_on_timeout=True
     )
   
   - Define index names as class constants:
     self.COMMITS_INDEX = "commits"
     self.TOUCHPOINTS_INDEX = "touchpoints"
   
   - Logger: self.logger = logging.getLogger(__name__)

3. Method: create_commits_index(self) -> bool:
   
   Purpose: Create the commits index with proper mappings
   
   Implementation:
   - Check if index exists:
     if self.client.indices.exists(index=self.COMMITS_INDEX):
         self.logger.info("Commits index already exists")
         return True
   
   - Define mapping:
     mapping = {
       "mappings": {
         "properties": {
           "repo": {"type": "keyword"},
           "commit_hash": {"type": "keyword"},
           "short_hash": {"type": "keyword"},
           "timestamp": {"type": "date"},
           "author": {"type": "keyword"},
           "author_email": {"type": "keyword"},
           "message": {"type": "text", "analyzer": "standard"},
           "files_changed": {"type": "keyword"},
           "insertions": {"type": "integer"},
           "deletions": {"type": "integer"},
           "diff_summary": {"type": "text"}
         }
       },
       "settings": {
         "number_of_shards": 1,
         "number_of_replicas": 0
       }
     }
   
   - Create index:
     self.client.indices.create(
       index=self.COMMITS_INDEX,
       body=mapping
     )
   
   - Return True on success
   
   Error handling:
   - Log errors
   - Return False on failure

4. Method: create_touchpoints_index(self) -> bool:
   
   Purpose: Track line-level changes over time
   
   Implementation:
   - Similar to commits but with mapping:
     {
       "repo": keyword,
       "file_path": keyword,
       "line_start": integer,
       "line_end": integer,
       "commit_hash": keyword,
       "change_type": keyword (added/modified/deleted),
       "timestamp": date,
       "author": keyword
     }

5. Method: index_commits(self, commits: List[Dict], repo_name: str) -> int:
   
   Purpose: Bulk index commits
   
   Implementation:
   - Transform commits to Elastic documents:
     actions = []
     for commit in commits:
         doc = {
           "_index": self.COMMITS_INDEX,
           "_id": f"{repo_name}:{commit['commit_hash']}",
           "_source": {
             "repo": repo_name,
             "commit_hash": commit["commit_hash"],
             "short_hash": commit["commit_hash"][:7],
             "timestamp": commit["timestamp"],
             "author": commit["author"],
             "message": commit["message"],
             "files_changed": commit.get("files_changed", []),
             "indexed_at": datetime.utcnow().isoformat()
           }
         }
         actions.append(doc)
   
   - Use bulk helper:
     from elasticsearch.helpers import bulk
     success, failed = bulk(
       self.client,
       actions,
       raise_on_error=False,
       stats_only=False
     )
   
   - Log results:
     self.logger.info(f"Indexed {success} commits, {len(failed)} failures")
   
   - Return number of successful indexes

6. Method: search_commits(
       self,
       repo: str,
       query: Optional[str] = None,
       author: Optional[str] = None,
       file_path: Optional[str] = None,
       from_date: Optional[str] = None,
       to_date: Optional[str] = None,
       size: int = 20
   ) -> List[Dict]:
   
   Purpose: Search commits with filters
   
   Implementation:
   - Build Elasticsearch query:
     must_clauses = [{"term": {"repo": repo}}]
     
     if query:
         must_clauses.append({
           "match": {
             "message": {
               "query": query,
               "operator": "or",
               "fuzziness": "AUTO"
             }
           }
         })
     
     if author:
         must_clauses.append({"term": {"author": author}})
     
     if file_path:
         must_clauses.append({"term": {"files_changed": file_path}})
     
     if from_date or to_date:
         date_range = {}
         if from_date:
             date_range["gte"] = from_date
         if to_date:
             date_range["lte"] = to_date
         must_clauses.append({"range": {"timestamp": date_range}})
     
     search_body = {
       "query": {
         "bool": {
           "must": must_clauses
         }
       },
       "sort": [{"timestamp": "desc"}],
       "size": size
     }
   
   - Execute search:
     response = self.client.search(
       index=self.COMMITS_INDEX,
       body=search_body
     )
   
   - Extract and return hits:
     hits = response["hits"]["hits"]
     return [hit["_source"] for hit in hits]

7. Method: get_commit_by_hash(self, repo: str, commit_hash: str) -> Optional[Dict]:
   
   Purpose: Get a specific commit
   
   Implementation:
   - Search by ID: f"{repo}:{commit_hash}"
   - Return document if found, None otherwise

8. Method: get_file_history(self, repo: str, file_path: str, size: int = 50) -> List[Dict]:
   
   Purpose: Get all commits that touched a file
   
   Implementation:
   - Search with file_path filter
   - Sort by timestamp descending
   - Return list of commits

9. Add health check method:
   def health_check(self) -> Dict[str, Any]:
       try:
           info = self.client.info()
           return {
               "status": "healthy",
               "cluster_name": info.get("cluster_name"),
               "version": info.get("version", {}).get("number")
           }
       except Exception as e:
           return {"status": "unhealthy", "error": str(e)}

10. Add singleton pattern:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Expected output:** Complete Elastic service module

---

## Hour 2-4: Data Ingestion

### Step 4: Create Ingestion Script

**Prompt for Claude Code:**
```
Create backend/scripts/ingest_demo_repos.py:

Purpose: Index multiple demo repos for testing

1. Import:
   - sys
   - os
   - git (GitPython)
   - pathlib
   - ElasticService
   - tempfile
   - logging

2. Setup logging

3. Function: extract_commits_from_repo(repo_path: str, repo_name: str) -> List[Dict]:
   
   Purpose: Extract all commit information from a git repo
   
   Implementation:
   - Use GitPython to get all commits:
     repo = git.Repo(repo_path)
     commits = []
     
     for commit in repo.iter_commits('--all', max_count=1000):
         commit_info = {
           "commit_hash": commit.hexsha,
           "author": commit.author.name,
           "author_email": commit.author.email,
           "timestamp": commit.committed_datetime.isoformat(),
           "message": commit.message.strip(),
           "files_changed": [item.a_path for item in commit.diff(commit.parents[0] if commit.parents else None)],
           "insertions": commit.stats.total["insertions"],
           "deletions": commit.stats.total["deletions"]
         }
         commits.append(commit_info)
     
     return commits
   
   Error handling:
   - Empty repos
   - Initial commits (no parents)
   - Corrupted git history

4. Function: ingest_repo(repo_url: str, repo_name: str) -> int:
   
   Purpose: Clone repo and index all commits
   
   Implementation:
   - Create temp directory
   - Clone repo:
     temp_dir = tempfile.mkdtemp()
     repo_path = os.path.join(temp_dir, "repo")
     git.Repo.clone_from(repo_url, repo_path, depth=100)  # Last 100 commits
   
   - Extract commits
   - Index to Elastic:
     elastic = ElasticService.get_instance()
     count = elastic.index_commits(commits, repo_name)
   
   - Cleanup temp directory
   - Return count

5. Main execution:
   
   Demo repos to index (small, public repos with clear history):
   
   DEMO_REPOS = [
       {
         "url": "https://github.com/pallets/flask",
         "name": "flask"
       },
       {
         "url": "https://github.com/django/django",
         "name": "django"
       },
       {
         "url": "https://github.com/fastapi/fastapi",
         "name": "fastapi"
       }
   ]
   
   For each repo:
   - Create indices (commits, touchpoints)
   - Ingest commits
   - Print progress
   - Print summary at end

6. Add command-line arguments:
   - --repo-url: Index a custom repo
   - --repo-name: Name for the repo
   - --all: Index all demo repos (default)

Run with:
```bash
python scripts/ingest_demo_repos.py --all
```

Or:
```bash
python scripts/ingest_demo_repos.py --repo-url https://github.com/user/repo --repo-name myrepo
```

Expected output:
```
Indexing flask...
  Extracted 500 commits
  Indexed 500 commits successfully
Indexing django...
  Extracted 1000 commits
  Indexed 1000 commits successfully
✓ Total: 1500 commits indexed across 2 repos
```
```

---

### Step 5: Run Ingestion & Verify

**Run the script:**
```bash
cd backend
python scripts/ingest_demo_repos.py --all
```

**Verify in Elastic Console (browser):**

1. Go to Elastic Cloud dashboard
2. Click your "bugrewind" project
3. Click "Dev Tools" in left sidebar
4. Run queries:

```json
// Check total commits
GET commits/_count

// See recent commits
GET commits/_search
{
  "size": 5,
  "sort": [{"timestamp": "desc"}]
}

// Search by keyword
GET commits/_search
{
  "query": {
    "match": {
      "message": "auth"
    }
  }
}

// Get commits for specific file
GET commits/_search
{
  "query": {
    "term": {
      "files_changed": "src/auth.py"
    }
  }
}
```

**Expected:** See your indexed commits in results

---

### Step 6: Add Elastic Endpoints to Backend

**Prompt for Claude Code:**
```
Create backend/app/routes/elastic.py:

Purpose: Expose Elastic search capabilities via REST API

1. Import:
   - FastAPI (APIRouter, Query)
   - ElasticService
   - typing

2. Create router:
   router = APIRouter(prefix="/elastic", tags=["elastic"])

3. GET /elastic/health endpoint:

@router.get("/health")
async def elastic_health():
    """Check Elastic connection status"""
    elastic = ElasticService.get_instance()
    return elastic.health_check()

4. GET /elastic/search endpoint:

@router.get("/search")
async def search_commits(
    repo: str,
    query: Optional[str] = None,
    author: Optional[str] = None,
    file_path: Optional[str] = None,
    size: int = Query(default=20, le=100)
):
    """
    Search commits across multiple dimensions.
    
    Examples:
    - /elastic/search?repo=flask&query=authentication
    - /elastic/search?repo=django&author=john&file_path=auth.py
    """
    elastic = ElasticService.get_instance()
    results = elastic.search_commits(
        repo=repo,
        query=query,
        author=author,
        file_path=file_path,
        size=size
    )
    return {
        "total": len(results),
        "results": results
    }

5. GET /elastic/repos endpoint:

@router.get("/repos")
async def list_repos():
    """Get list of all indexed repos"""
    elastic = ElasticService.get_instance()
    
    # Aggregation query to get unique repos
    agg_query = {
        "size": 0,
        "aggs": {
            "repos": {
                "terms": {
                    "field": "repo",
                    "size": 100
                }
            }
        }
    }
    
    response = elastic.client.search(
        index=elastic.COMMITS_INDEX,
        body=agg_query
    )
    
    repos = [
        bucket["key"] 
        for bucket in response["aggregations"]["repos"]["buckets"]
    ]
    
    return {"repos": repos}

6. GET /elastic/stats endpoint:

@router.get("/stats")
async def get_stats():
    """Get indexing statistics"""
    elastic = ElasticService.get_instance()
    
    # Get total commits
    total = elastic.client.count(index=elastic.COMMITS_INDEX)
    
    # Get commits by repo
    agg_query = {
        "size": 0,
        "aggs": {
            "by_repo": {
                "terms": {"field": "repo", "size": 50}
            }
        }
    }
    
    response = elastic.client.search(
        index=elastic.COMMITS_INDEX,
        body=agg_query
    )
    
    by_repo = {
        bucket["key"]: bucket["doc_count"]
        for bucket in response["aggregations"]["by_repo"]["buckets"]
    }
    
    return {
        "total_commits": total["count"],
        "by_repo": by_repo
    }
```

**Update app/main.py to include this router:**
```python
from app.routes import elastic
app.include_router(elastic.router)
```

**Test the endpoints:**
```bash
curl http://localhost:8000/elastic/health
curl "http://localhost:8000/elastic/search?repo=flask&query=auth"
curl http://localhost:8000/elastic/stats
```

---

## Hour 4-8: Advanced Search Features

### Step 7: Semantic Search Helper

**Prompt for Claude Code:**
```
In backend/app/services/elastic_service.py, add method:

def semantic_search(
    self,
    repo: str,
    natural_query: str,
    size: int = 10
) -> List[Dict]:
    """
    Semantic search using Elastic's text matching with boosting.
    
    Example: "bug with authentication after refactor"
    Will search message field with intelligent scoring.
    """
    
    Implementation:
    - Build multi-match query:
      query = {
        "query": {
          "bool": {
            "must": [
              {"term": {"repo": repo}},
              {
                "multi_match": {
                  "query": natural_query,
                  "fields": ["message^3", "author^1"],
                  "type": "best_fields",
                  "fuzziness": "AUTO",
                  "operator": "or"
                }
              }
            ]
          }
        },
        "size": size,
        "sort": [
          {"_score": "desc"},
          {"timestamp": "desc"}
        ]
      }
    
    - Execute and return results with scores:
      response = self.client.search(index=self.COMMITS_INDEX, body=query)
      
      return [
        {
          **hit["_source"],
          "relevance_score": hit["_score"]
        }
        for hit in response["hits"]["hits"]
      ]
    
    This gives better results for natural language queries.
```

**Add endpoint in elastic.py:**
```python
@router.get("/semantic-search")
async def semantic_search(
    repo: str,
    query: str,
    size: int = Query(default=10, le=50)
):
    """
    Search commits using natural language.
    
    Example: /elastic/semantic-search?repo=flask&query=fix auth bug after refactor
    """
    elastic = ElasticService.get_instance()
    results = elastic.semantic_search(repo, query, size)
    return {"results": results}
```

---

### Step 8: Create Search Analytics

**Prompt for Claude Code:**
```
In backend/app/routes/elastic.py, add endpoint:

@router.get("/analytics/timeline")
async def commit_timeline(
    repo: str,
    file_path: Optional[str] = None,
    interval: str = Query(default="1M", regex="^[0-9]+[dwMy]$")
):
    """
    Get commit frequency over time.
    
    interval options:
    - 1d: daily
    - 1w: weekly
    - 1M: monthly (default)
    - 1y: yearly
    """
    
    elastic = ElasticService.get_instance()
    
    # Build aggregation query
    must_clauses = [{"term": {"repo": repo}}]
    if file_path:
        must_clauses.append({"term": {"files_changed": file_path}})
    
    agg_query = {
        "size": 0,
        "query": {
            "bool": {"must": must_clauses}
        },
        "aggs": {
            "commits_over_time": {
                "date_histogram": {
                    "field": "timestamp",
                    "calendar_interval": interval,
                    "format": "yyyy-MM-dd"
                }
            }
        }
    }
    
    response = elastic.client.search(
        index=elastic.COMMITS_INDEX,
        body=agg_query
    )
    
    buckets = response["aggregations"]["commits_over_time"]["buckets"]
    
    timeline = [
        {
            "date": bucket["key_as_string"],
            "count": bucket["doc_count"]
        }
        for bucket in buckets
    ]
    
    return {"timeline": timeline}
```

This will be useful for visualizing when bugs were introduced!

---

## Hour 8-14: Postman Flow Creation

### Step 9: Set Up Postman Account

**Manual steps:**

1. Go to https://www.postman.com
2. Sign up (use Google auth for speed)
3. Skip onboarding tour
4. Create new Workspace:
   - Click "Workspaces" dropdown (top left)
   - "Create Workspace"
   - Name: `BugRewind`
   - Visibility: **Public** (important for judges!)
   - Description: "AI-powered git archaeology for bug origins"
   - Click "Create"

**Expected result:** Empty public workspace

---

### Step 10: Expose Backend with ngrok

**Install ngrok (if not already):**
```bash
# On Mac:
brew install ngrok

# On Linux:
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Sign up at ngrok.com and get auth token
ngrok config add-authtoken YOUR_TOKEN
```

**Start ngrok:**
```bash
# In a new terminal (keep it running):
ngrok http 8000

# Copy the HTTPS URL shown (looks like: https://abc123.ngrok-free.app)
```

**Save this URL** - you'll need it for Postman

**Test it:**
```bash
curl https://YOUR_NGROK_URL/health
# Should return: {"status": "healthy", "version": "1.0.0"}
```

---

### Step 11: Create Basic Flow Structure

**In Postman workspace:**

1. Click "Flows" in left sidebar
2. Click "Create Flow" button
3. Name: `BugRewind Agent`
4. Click "Create"

**Add blocks (drag from left panel):**

5. **Start block** (already there by default)
   - This receives the input

6. **AI Agent block** (search for "AI Agent" in blocks)
   - Drag onto canvas
   - Connect Start → AI Agent

7. **Send Request block** × 3 (search for "Send Request")
   - These will call: Elastic, Backend, GitHub
   - Drag 3 of them onto canvas

8. **Log block** × 3 (search for "Log")
   - For debugging each API call

9. **Select block** × 2 (search for "Select")
   - For conditional logic

10. **Output block** (at the end)
    - Returns final result

**Layout on canvas:**
```
Start 
  → AI Agent (planning)
    → Select (search Elastic or go direct?)
      → [Path A] Send Request (Elastic)
        → Log
      → [Path B] Skip Elastic
    → Send Request (Backend /analyze-bug)
      → Log
    → Select (create PR or just return?)
      → [Path A] Send Request (GitHub PR)
        → Log
      → [Path B] Skip PR
    → Output
```

**Don't configure yet** - just get the structure

**Save the flow** (Ctrl+S or top-right Save button)

---

### Step 12: Configure AI Agent Block

**Click the AI Agent block:**

**Settings:**

**Prompt template:**
```
You are a bug analysis planning agent. Given a bug description, decide the best approach:

Input from user:
{{input.bug_description}}
{{input.repo_url}}
{{input.file_path}}

Your tasks:
1. Analyze if we should search Elastic commit history first or go directly to git blame
   - Search Elastic if: bug description has specific keywords (auth, database, api, etc.)
   - Skip Elastic if: file_path and line_hint are already provided
2. Extract key terms for commit search
3. Determine if we should auto-create a PR or just return analysis

Return ONLY a JSON object:
{
  "action": "search_elastic" or "direct_analyze",
  "search_terms": ["keyword1", "keyword2"],
  "should_create_pr": true or false,
  "confidence": 0.85,
  "reasoning": "brief explanation"
}

Return only valid JSON, no markdown, no explanation outside the JSON.
```

**Model selection:**
- Choose: GPT-4 or Claude (whichever is available)
- Max tokens: 500
- Temperature: 0.3 (low for consistency)

**Save response as variable:**
- Variable name: `agent_plan`

**Connect to next block:**
- Drag from AI Agent output → Select block

---

### Step 13: Configure Select Block (Elastic Path)

**Click first Select block:**

**Condition:**
```javascript
{{agent_plan.action}} == "search_elastic"
```

**True path:**
- Connect to Send Request (Elastic)

**False path:**
- Connect directly to Send Request (Backend)

This decides whether to search Elastic first or skip it.

---

### Step 14: Configure Send Request (Elastic Search)

**Click Send Request block (for Elastic):**

**Method:** GET

**URL:**
```
{{backend_url}}/elastic/semantic-search
```

**Query parameters:** (click "Add Parameter" for each)
- Key: `repo`, Value: `{{extract_repo_name(input.repo_url)}}`
- Key: `query`, Value: `{{agent_plan.search_terms}}`
- Key: `size`, Value: `10`

**Headers:**
- Content-Type: `application/json`

**Save response as:** `elastic_results`

**Connect output to Log block**

**Note:** We need to add `backend_url` as a workspace variable:
- Click workspace name (top right)
- Click "Variables" tab
- Add variable:
  - Name: `backend_url`
  - Value: Your ngrok URL (e.g., `https://abc123.ngrok-free.app`)
  - Type: Default

---

### Step 15: Configure Log Block (Elastic)

**Click Log block after Elastic request:**

**Message:**
```
Elastic search completed
Found: {{elastic_results.total}} commits
Top result: {{elastic_results.results[0].message}}
```

**Level:** Info

**Connect output to next Send Request (Backend)**

---

### Step 16: Configure Send Request (Backend Analyze)

**Click Send Request block (main analysis):**

**Method:** POST

**URL:**
```
{{backend_url}}/api/analyze-bug
```

**Headers:**
- Content-Type: `application/json`

**Body:** (select "Raw JSON")
```json
{
  "repo_url": "{{input.repo_url}}",
  "bug_description": "{{input.bug_description}}",
  "file_path": "{{input.file_path}}",
  "line_hint": "{{input.line_hint}}"
}
```

**Timeout:** 120000 (120 seconds - git operations can be slow)

**Save response as:** `analysis_results`

**Error handling:**
- Click "Add error handler"
- On error, connect to Log block
- Log message: `Backend error: {{error.message}}`

**Connect output to Log block**

---

### Step 17: Configure Log Block (Backend)

**Click Log block after Backend request:**

**Message:**
```
Analysis completed
First bad commit: {{analysis_results.first_bad_commit}}
Root cause: {{analysis_results.analysis.root_cause}}
Confidence: {{analysis_results.analysis.confidence}}
```

**Connect output to Select block (PR decision)**

---

### Step 18: Configure Select Block (PR Decision)

**Click second Select block:**

**Condition:**
```javascript
{{agent_plan.should_create_pr}} == true && {{analysis_results.analysis.confidence}} > 0.7
```

Only create PR if:
- Agent decided we should
- AND Claude is confident (>70%)

**True path:** Connect to Send Request (GitHub PR)

**False path:** Skip directly to Output

---

### Step 19: Configure Send Request (GitHub PR)

**Click Send Request block (PR creation):**

**Method:** POST

**URL:**
```
{{backend_url}}/api/create-pr
```

**Headers:**
- Content-Type: `application/json`

**Body:**
```json
{
  "repo_url": "{{input.repo_url}}",
  "branch_name": "bugrewind-fix-{{$timestamp}}",
  "patch_content": "{{analysis_results.analysis.minimal_patch}}",
  "title": "Fix: {{analysis_results.analysis.root_cause | truncate(60)}}",
  "description": "## BugRewind Automated Fix\n\n**Root Cause:**\n{{analysis_results.analysis.root_cause}}\n\n**Developer Intent:**\n{{analysis_results.analysis.developer_intent}}\n\n**Suggested Patch:**\n```diff\n{{analysis_results.analysis.minimal_patch}}\n```\n\n**First Bad Commit:** {{analysis_results.first_bad_commit}}\n**Analysis Confidence:** {{analysis_results.analysis.confidence}}"
}
```

**Save response as:** `pr_result`

**Error handling:**
- On error → Log: `PR creation failed: {{error.message}}`

**Connect to Log block**

---

### Step 20: Configure Final Log & Output

**Log block (after PR):**
```
PR created successfully
URL: {{pr_result.pr_url}}
Branch: {{pr_result.branch_name}}
```

**Output block:**

**Format final response:**
```json
{
  "success": true,
  "agent_decision": {
    "action": "{{agent_plan.action}}",
    "reasoning": "{{agent_plan.reasoning}}",
    "confidence": "{{agent_plan.confidence}}"
  },
  "elastic_search": {
    "performed": "{{agent_plan.action == 'search_elastic'}}",
    "results_count": "{{elastic_results.total || 0}}",
    "top_commit": "{{elastic_results.results[0].commit_hash || 'N/A'}}"
  },
  "analysis": {
    "first_bad_commit": "{{analysis_results.first_bad_commit}}",
    "root_cause": "{{analysis_results.analysis.root_cause}}",
    "developer_intent": "{{analysis_results.analysis.developer_intent}}",
    "confidence": "{{analysis_results.analysis.confidence}}",
    "commits_analyzed": "{{analysis_results.commits.length}}"
  },
  "pull_request": {
    "created": "{{pr_result != null}}",
    "url": "{{pr_result.pr_url || 'Not created'}}",
    "branch": "{{pr_result.branch_name || 'N/A'}}"
  },
  "metadata": {
    "timestamp": "{{$timestamp}}",
    "execution_time_ms": "{{$duration}}",
    "repo": "{{input.repo_url}}",
    "file": "{{input.file_path}}"
  }
}
```

**Save the flow**

---

## Hour 14-16: Test & Debug Flow

### Step 21: Run Flow with Test Data

**Click "Run" button (top right)**

**Enter test input:**
```json
{
  "repo_url": "https://github.com/pallets/flask",
  "bug_description": "Authentication middleware returns 401 unexpectedly after recent refactor",
  "file_path": "src/flask/auth.py",
  "line_hint": 45
}
```

**Click "Run Flow"**

**Watch execution:**
- Each block will light up as it executes
- Click on blocks to see their outputs
- Check Log blocks for debugging info

**Expected issues and fixes:**

**If AI Agent fails:**
- Check API key is configured in Postman settings
- Simplify prompt (remove complex logic)

**If Elastic search fails:**
- Check backend_url variable is correct
- Test the URL directly in browser: `https://your-ngrok/elastic/health`

**If Backend analyze fails:**
- Check request body format
- Look at backend logs: `python app/main.py` terminal
- Common issue: repo cloning timeout

**If JSON parsing fails:**
- Add JSON validation in Select blocks
- Use default values: `{{variable || "default"}}`

**Debug tips:**
1. Add more Log blocks to see intermediate values
2. Use Select blocks with conditions like `{{variable != null}}`
3. Check Postman Console (bottom panel) for full request/response

**Keep iterating until flow completes successfully!**

---

### Step 22: Add Error Recovery

**Make flow more robust:**

**Add error paths from each Send Request:**

1. After Elastic request fails:
   - Connect error output to Log: "Elastic search failed, proceeding with direct analysis"
   - Connect Log to Backend request (fallback path)

2. After Backend request fails:
   - Connect to Log: "Analysis failed: {{error.message}}"
   - Connect to Output with error response:
     ```json
     {
       "success": false,
       "error": "{{error.message}}",
       "suggestion": "Check repo URL and file path"
     }
     ```

3. After PR request fails:
   - Connect to Log: "PR creation skipped due to error"
   - Continue to Output (analysis still succeeded)

**Test with bad inputs:**
```json
{
  "repo_url": "https://github.com/invalid/repo",
  "bug_description": "test",
  "file_path": "nonexistent.py"
}
```

Should get graceful error, not crash.

---

## Hour 16-18: Deploy as Action

### Step 23: Deploy Flow as Action

**In Postman Flow editor:**

1. Click Flow menu (top left, next to flow name)
2. Click "Deploy"
3. Select "Deploy as Action"

**Configure Action:**

**Name:** `BugRewind Analyzer`

**Description:**
```
Analyzes git history to find bug origins using AI.

Features:
- Intelligent commit search via Elastic
- Claude-powered root cause analysis
- Automatic PR creation with fixes

Perfect for: Debugging production issues, understanding technical debt, automated triage
```

**API Endpoint Settings:**
- Enable authentication: No (for hackathon demo)
- Rate limiting: 100 requests/hour
- Timeout: 180 seconds

**Required input fields:**
```json
{
  "repo_url": {
    "type": "string",
    "description": "GitHub repository URL",
    "required": true,
    "example": "https://github.com/user/repo"
  },
  "bug_description": {
    "type": "string",
    "description": "Description of the bug",
    "required": true,
    "example": "Auth fails with 401 after refactor"
  },
  "file_path": {
    "type": "string",
    "description": "Path to the file with the bug",
    "required": true,
    "example": "src/auth.py"
  },
  "line_hint": {
    "type": "number",
    "description": "Line number where bug occurs (optional)",
    "required": false,
    "example": 45
  }
}
```

**Click "Deploy"**

**Copy the Action URL** - looks like:
```
https://api.postman.com/actions/12345abc-6789-def0-1234-567890abcdef/run
```

**Save this URL** - this is your deliverable!

---

### Step 24: Test Action URL

**Test with curl:**
```bash
curl -X POST 'https://api.postman.com/actions/YOUR_ACTION_ID/run' \
  -H 'Content-Type: application/json' \
  -d '{
    "repo_url": "https://github.com/pallets/flask",
    "bug_description": "Authentication middleware fails after refactor",
    "file_path": "src/flask/auth.py",
    "line_hint": 45
  }'
```

**Expected response:**
```json
{
  "success": true,
  "agent_decision": { ... },
  "elastic_search": { ... },
  "analysis": {
    "first_bad_commit": "abc123",
    "root_cause": "Removed null check in refactor",
    ...
  },
  "pull_request": {
    "created": true,
    "url": "https://github.com/.../pull/123"
  },
  "metadata": { ... }
}
```

**If it fails:**
- Check ngrok is still running
- Check backend is running
- Look at Flow execution logs in Postman
- Verify all workspace variables are set

---

### Step 25: Create Action Documentation

**In Postman workspace:**

1. Create new Collection: "BugRewind API"
2. Add example requests:

**Request 1: Basic Analysis**
```
POST {{ACTION_URL}}
Body:
{
  "repo_url": "https://github.com/pallets/flask",
  "bug_description": "Auth bug",
  "file_path": "src/auth.py"
}
```

**Request 2: With Line Hint**
```
POST {{ACTION_URL}}
Body:
{
  "repo_url": "https://github.com/django/django",
  "bug_description": "Database connection timeout",
  "file_path": "django/db/backends/base/base.py",
  "line_hint": 234
}
```

**Request 3: OCR-based Analysis**
(Call backend directly first to get file info)
```
POST {{backend_url}}/api/analyze-bug-from-image
Body:
{
  "image_data": "base64_encoded_screenshot",
  "bug_description": "Got this error, not sure where"
}
```

3. Add descriptions and expected responses
4. Make collection public

---

## Hour 18-22: Documentation & Polish

### Step 26: Create Workspace README

**In Postman workspace:**

1. Click workspace name → "Overview" tab
2. Click "Edit Description"
3. Add comprehensive README:

```markdown
# BugRewind - AI-Powered Git Archaeology

[![Cal Hacks 12.0](https://img.shields.io/badge/Cal%20Hacks-12.0-blue)]()
[![Elastic](https://img.shields.io/badge/Powered%20by-Elastic-blue)]()
[![Postman](https://img.shields.io/badge/Built%20with-Postman%20Flows-orange)]()

## What It Does

BugRewind uses AI and git archaeology to trace bugs back to their origin commit, explain what went wrong, and suggest fixes automatically.

### Features

🔍 **Smart Commit Search**: Searches Elastic-indexed git history using natural language
🤖 **AI Planning**: Postman AI Agent decides the optimal analysis strategy
🧠 **Root Cause Analysis**: Claude explains exactly what went wrong and why
📸 **OCR Support**: Upload error screenshots for automatic file/line detection
🔧 **Auto PR Creation**: Generates pull requests with suggested fixes

## Architecture

```
User Input
    ↓
AI Agent (Planning)
    ↓
Elastic Search (Commit History) [Optional]
    ↓
Backend Analysis (Git Blame + Claude)
    ↓
GitHub PR Creation [Optional]
    ↓
Structured Results
```

## How to Use

### Option 1: Call the Action Directly

```bash
curl -X POST 'https://api.postman.com/actions/YOUR_ACTION_ID/run' \
  -H 'Content-Type: application/json' \
  -d '{
    "repo_url": "https://github.com/user/repo",
    "bug_description": "Description of the issue",
    "file_path": "path/to/file.py",
    "line_hint": 45
  }'
```

### Option 2: Use the Postman Collection

See [BugRewind API Collection](link) for example requests.

### Option 3: Use the Web UI

Visit [Frontend URL] for a visual interface.

## APIs Used

1. **Elastic Serverless** - Indexed commit history search
   - 3 demo repos indexed
   - ~1500 commits searchable
   - Semantic search with relevance scoring

2. **Anthropic Claude** - Root cause analysis
   - Model: claude-sonnet-4-20250514
   - Analyzes commit context and developer intent
   - Generates fix suggestions

3. **GitHub REST API** - PR automation
   - Branch creation
   - Pull request generation

4. **DeepSeek OCR** - Error screenshot analysis
   - Extracts text from images
   - Identifies file paths and line numbers

## Example Output

```json
{
  "success": true,
  "analysis": {
    "first_bad_commit": "a3f9b2c",
    "root_cause": "Removed null check during refactor, causing NPE when user is null",
    "developer_intent": "Simplify auth flow by removing redundant checks",
    "confidence": 0.92
  },
  "pull_request": {
    "created": true,
    "url": "https://github.com/user/repo/pull/123"
  }
}
```

## Setup (For Developers)

### Prerequisites
- Python 3.9+
- Elastic Serverless account
- Anthropic API key
- GitHub token

### Installation

```bash
# Clone repo
git clone https://github.com/your-team/bugrewind

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Fill in your API keys

# Run backend
python app/main.py
```

### Index Demo Repos

```bash
python scripts/ingest_demo_repos.py --all
```

## Testing

See [Collection](link) for test requests.

**Test repos indexed:**
- flask (500 commits)
- django (1000 commits)
- fastapi (400 commits)

## Team

Built by [Your Team] for Cal Hacks 12.0

## Links

- **Action URL**: [Your Postman Action URL]
- **Backend**: [ngrok URL] (temporary)
- **Frontend**: [Vercel URL]
- **GitHub**: [Repo URL]
- **Video Demo**: [YouTube URL]

## Tech Stack

- **Backend**: FastAPI (Python)
- **Orchestration**: Postman Flows + AI Agent
- **Search**: Elastic Serverless
- **AI**: Anthropic Claude Sonnet 4
- **OCR**: DeepSeek
- **Version Control**: GitHub API
- **Frontend**: Next.js (by Dev C)
```

---

### Step 27: Screenshot Everything

**Take these screenshots for submission:**

1. **Flow Canvas** (full view)
   - Show all blocks connected
   - Zoom out to fit everything
   - Save as `postman-flow-architecture.png`

2. **AI Agent Block Configuration**
   - Show the prompt
   - Save as `ai-agent-config.png`

3. **Action Deployment Page**
   - Show Action URL and settings
   - Save as `action-deployment.png`

4. **Successful Execution**
   - Run flow with real data
   - Show all green blocks
   - Save as `flow-execution-success.png`

5. **Elastic Dashboard**
   - Show indexed commits
   - Show search query results
   - Save as `elastic-indexed-data.png`

6. **Sample API Response**
   - Pretty-print JSON response
   - Save as `sample-response.json`

Save all to `/demo` folder in repo.

---

### Step 28: Create Video Demo

**Record 90-second screen recording:**

**Script:**
```
[0:00-0:10] Opening
"This is BugRewind - AI-powered git archaeology for bugs."

[0:10-0:25] Show Postman Flow
"Here's our Postman Flow. An AI Agent analyzes the bug description, 
decides whether to search Elastic commit history, calls our backend 
for git blame analysis, gets Claude's explanation, and optionally 
creates a PR."

[0:25-0:40] Run the Flow
"Let me run it with a real bug..."
[Show input, click Run]
"The AI Agent decides to search Elastic first..."
[Point to blocks lighting up]

[0:40-0:60] Show Results
"Here's the output: it found the exact commit that introduced the bug,
Claude explained what went wrong, and it created a pull request with
the fix."
[Show JSON output]

[0:60-0:75] Show Action URL
"We deployed this as a Postman Action with a public URL, so you can
call it from anywhere."
[Show curl command and response]

[0:75-0:90] Show Elastic
"All of this is powered by Elastic Serverless, which we use to index
and search git history. Here you can see the indexed commits."
[Show Elastic dashboard]

"Thanks for watching!"
```

**Upload to YouTube as Unlisted** - save URL

---

### Step 29: Integration Testing with Dev A & C

**Coordinate with team:**

**Test sequence:**

1. **Dev A**: Backend is running, exposed via ngrok
2. **Dev B**: Postman Flow calls backend successfully
3. **Dev C**: Frontend calls backend AND can trigger Postman Action

**Full integration test:**
```
User fills form in Frontend
    ↓
Frontend → Backend /analyze-bug
    ↓
Backend → Git operations + Claude
    ↓
Results return to Frontend
    ↓
User clicks "Run Full Analysis"
    ↓
Frontend → Postman Action URL
    ↓
Postman Flow → Elastic + Backend + GitHub
    ↓
Complete analysis with PR link
```

**Test both paths work!**

---

### Step 30: Final Checklist

**By hour 22, verify you have:**

- [x] Elastic Serverless project with indexed data
- [x] ElasticService with search capabilities
- [x] 3+ demo repos indexed (~1500 commits)
- [x] Elastic API endpoints in backend
- [x] Postman Flow with AI Agent orchestration
- [x] Error handling in all paths
- [x] Deployed as public Action with URL
- [x] Workspace README with examples
- [x] Sample requests in collection
- [x] Screenshots of everything
- [x] Video demo recorded
- [x] Integration tested with Dev A's backend
- [x] Action URL works from curl
- [x] Logs visible for debugging

**Deliverables for judges:**

1. **Action URL**: `https://api.postman.com/actions/YOUR_ID/run`
2. **Workspace URL**: `https://www.postman.com/YOUR_WORKSPACE/bugrewind`
3. **Sample input/output**: In workspace README
4. **Demo video**: YouTube link

---

## Emergency Troubleshooting

**If Elastic fails:**
- Fall back to direct git operations
- Skip Elastic search in Flow (always take "direct" path)
- Still counts for Postman prize

**If Postman AI Agent is buggy:**
- Replace with simple Select block that checks for keywords
- Hard-code the decision logic
- Still functional, just less "intelligent"

**If Action deployment fails:**
- Share the Flow via workspace link instead
- Judges can run it manually
- Document that you attempted deployment

**If ngrok URL changes:**
- Update `backend_url` variable in Postman workspace
- Re-run Flow to verify
- Update documentation

---

## Pro Tips

1. **Keep ngrok running** - if it restarts, URL changes and everything breaks
2. **Test incrementally** - don't wait until the end to test the full flow
3. **Use Log blocks everywhere** - they're your debugging savior
4. **Save often** - Postman auto-saves but force-save (Ctrl+S) to be safe
5. **Make workspace public early** - easier to share with team and judges

---

**You've got this! By hour 22 you'll have a working Postman Action that orchestrates multiple AI services to solve real bugs. This is your differentiator - the novel orchestration layer!**

🚀 Go build something awesome!
```

