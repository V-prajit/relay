# Snowflake Integration - Quick Start Guide

## 🎉 What's Been Implemented

You now have a **complete Snowflake integration** with the following features:

### ✅ Core Features
1. **Data Warehouse Storage**
   - Store commit history across all repositories
   - Store bug analysis results
   - Track file-level changes (touchpoints)
   - Commit sentiment tracking

2. **Snowflake Cortex AI Functions**
   - `COMPLETE()` - AI text generation for bug analysis
   - `SENTIMENT()` - Analyze commit message sentiment, detect panic fixes
   - `SUMMARIZE()` - Summarize long commit messages
   - `EXTRACT_ANSWER()` - Extract specific info from commits

3. **Cortex Search**
   - Semantic/vector search through commit history
   - Natural language queries
   - Better than keyword search

4. **Time Travel**
   - Query historical states of your data
   - Analyze how bug detection evolved over time

5. **Analytics**
   - Repository statistics
   - Panic fix detection
   - Author activity tracking

### 📁 Files Created

```
backend/
├── app/
│   ├── services/
│   │   └── snowflake_service.py    ← Core Snowflake service (700+ lines)
│   └── routes/
│       └── snowflake.py             ← REST API endpoints (600+ lines)
├── test_snowflake_integration.py    ← Test script
├── requirements.txt                 ← Updated with snowflake packages
└── .env.example                     ← Updated with Snowflake config

SNOWFLAKE_INTEGRATION.md             ← Complete implementation guide
SNOWFLAKE_QUICKSTART.md              ← This file
```

### 🔌 API Endpoints Created

All endpoints are prefixed with `/api/snowflake`:

**Health & Status:**
- `GET /api/snowflake/health` - Check connection status

**Commit Operations:**
- `POST /api/snowflake/commits` - Insert single commit
- `POST /api/snowflake/commits/bulk` - Bulk insert commits
- `GET /api/snowflake/commits/search` - Search commits with filters

**Cortex LLM:**
- `POST /api/snowflake/cortex/complete` - AI text generation
- `GET /api/snowflake/cortex/sentiment/{commit_id}` - Sentiment analysis
- `GET /api/snowflake/cortex/summarize/{commit_id}` - Summarize commit
- `GET /api/snowflake/cortex/extract/{commit_id}` - Extract info from commit

**Cortex Search:**
- `GET /api/snowflake/cortex/search` - Semantic search through commits

**Bug Analysis:**
- `POST /api/snowflake/analysis` - Store bug analysis results
- `GET /api/snowflake/analysis/history` - Get analysis history

**Analytics:**
- `GET /api/snowflake/analytics/panic-fixes` - Find panic fixes
- `GET /api/snowflake/analytics/stats` - Repository statistics

**Time Travel:**
- `GET /api/snowflake/time-travel/{table}` - Query historical data

---

## 🚀 Next Steps to Get Running

### Step 1: Create Snowflake Account (5 minutes)

1. Go to https://signup.snowflake.com/
2. Sign up for **30-day free trial**
3. Choose:
   - Cloud: **AWS**
   - Region: **US East (N. Virginia)**
   - Edition: **Enterprise** (needed for Cortex)

### Step 2: Run SQL Setup (5 minutes)

Open Snowflake web UI and run all the SQL commands from:
**`SNOWFLAKE_INTEGRATION.md`** (section: "Set Up Snowflake Objects")

This creates:
- Database: `BUGREWIND`
- Schema: `GIT_ANALYSIS`
- Warehouse: `BUGREWIND_WH`
- Tables: `COMMITS`, `BUG_ANALYSIS`, `COMMIT_SENTIMENT`, `FILE_TOUCHPOINTS`
- Cortex Search Service: `COMMIT_SEARCH`

### Step 3: Configure Environment (2 minutes)

1. Copy `.env.example` to `.env`:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Edit `.env` and add your Snowflake credentials:
   ```env
   # Snowflake Configuration
   SNOWFLAKE_ACCOUNT=abc12345.us-east-1
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_DATABASE=BUGREWIND
   SNOWFLAKE_SCHEMA=GIT_ANALYSIS
   SNOWFLAKE_WAREHOUSE=BUGREWIND_WH
   SNOWFLAKE_ROLE=PUBLIC

   # Enable features
   ENABLE_SNOWFLAKE=true
   ENABLE_CORTEX_LLM=true
   ENABLE_CORTEX_SEARCH=true
   ```

   **To find your account identifier:**
   - In Snowflake UI, click your name (top right)
   - Click "Account" → Copy the account identifier
   - Format: `abc12345.region` (e.g., `xy12345.us-east-1`)

### Step 4: Install Dependencies (1 minute)

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `snowflake-connector-python==3.6.0`
- `snowflake-sqlalchemy==1.5.1`

### Step 5: Test Integration (2 minutes)

```bash
cd backend
python test_snowflake_integration.py
```

Expected output:
```
✓ Connected to Snowflake!
✓ Sample commit inserted successfully!
✓ Found commits
✓ Sentiment analysis successful!
✓ Cortex search returned results
✓ Repository statistics retrieved!

🎉 All tests passed!
```

### Step 6: Start Backend (1 minute)

```bash
cd backend
python app/main.py
```

You should see:
```
✓ Snowflake routes loaded
BugRewind API Starting
API documentation: http://localhost:8000/docs
```

### Step 7: Try the API (1 minute)

Open http://localhost:8000/docs in your browser

Try these endpoints:
1. **Health Check**: `GET /api/snowflake/health`
2. **Insert Commit**: `POST /api/snowflake/commits` (use example from docs)
3. **Search**: `GET /api/snowflake/commits/search?repo_name=test/bugrewind`

---

## 🎯 Usage Examples

### Example 1: Store Commits from Git Analysis

```python
import requests

# After analyzing a repo with git, store commits in Snowflake
commits = [
    {
        "commit_hash": "abc123...",
        "author": "John Doe",
        "message": "Fix authentication bug",
        "timestamp": "2024-01-15T10:30:00",
        "files_changed": ["src/auth.py"],
        "insertions": 10,
        "deletions": 5
    },
    # ... more commits
]

response = requests.post(
    "http://localhost:8000/api/snowflake/commits/bulk",
    json={
        "repo_name": "myorg/myrepo",
        "commits": commits
    }
)

print(f"Inserted {response.json()['inserted_count']} commits")
```

### Example 2: Semantic Search for Bug-Related Commits

```python
# Search for commits related to authentication issues
response = requests.get(
    "http://localhost:8000/api/snowflake/cortex/search",
    params={
        "query": "authentication bug fix security issue",
        "repo_name": "myorg/myrepo",
        "limit": 10
    }
)

results = response.json()["results"]
for commit in results:
    print(f"{commit['COMMIT_ID'][:7]}: {commit['MESSAGE']}")
    print(f"  Relevance: {commit['SEARCH_SCORE']}")
```

### Example 3: Analyze Commit Sentiment

```python
# Find commits that might be panic fixes
commit_id = "abc123..."

response = requests.get(
    f"http://localhost:8000/api/snowflake/cortex/sentiment/{commit_id}"
)

sentiment = response.json()
if sentiment["is_panic_fix"]:
    print(f"⚠️ Panic fix detected! Score: {sentiment['sentiment_score']}")
```

### Example 4: Store Bug Analysis Results

```python
# After Claude analyzes a bug, store the results
analysis = {
    "repo_name": "myorg/myrepo",
    "bug_description": "Auth fails with 401 after refactor",
    "file_path": "src/auth.py",
    "line_number": 45,
    "first_bad_commit": "abc123...",
    "root_cause": "Removed null check during refactor",
    "developer_intent": "Simplify authentication flow",
    "suggested_fix": "Add null check before user.auth()",
    "confidence": 0.92,
    "ai_model": "claude-sonnet-4",
    "execution_time_ms": 5234
}

response = requests.post(
    "http://localhost:8000/api/snowflake/analysis",
    json=analysis
)

print(f"Analysis stored: {response.json()['analysis_id']}")
```

### Example 5: Get Repository Statistics

```python
response = requests.get(
    "http://localhost:8000/api/snowflake/analytics/stats",
    params={"repo_name": "myorg/myrepo"}
)

stats = response.json()["statistics"]
print(f"Total commits: {stats['TOTAL_COMMITS']}")
print(f"Unique authors: {stats['UNIQUE_AUTHORS']}")
print(f"Lines added: +{stats['TOTAL_INSERTIONS']}")
print(f"Lines removed: -{stats['TOTAL_DELETIONS']}")
```

---

## 🔄 Integration with Existing Features

### Replace Elasticsearch with Snowflake

Your DEV_B.md guide uses Elasticsearch. You can now use Snowflake instead:

**Before (Elasticsearch):**
```python
elastic = ElasticService.get_instance()
results = elastic.search_commits(repo="myrepo", query="auth")
```

**After (Snowflake with Cortex):**
```python
snowflake = SnowflakeService.get_instance()
results = snowflake.cortex_search_commits(query="authentication issues", repo_name="myrepo")
```

**Benefits:**
- Better semantic search (understands intent)
- Built-in AI functions
- Data warehouse for analytics
- Time Travel queries
- Enterprise-grade reliability

### Update Postman Flow

In your Postman Flow (from DEV_B.md), replace the Elastic endpoints with Snowflake:

**Old:** `{{backend_url}}/elastic/semantic-search`
**New:** `{{backend_url}}/api/snowflake/cortex/search`

---

## 🎓 Advanced Features

### Time Travel Example

Query commits as they existed yesterday:
```bash
curl "http://localhost:8000/api/snowflake/time-travel/COMMITS?timestamp=2024-01-20T00:00:00&conditions=REPO_NAME='myrepo'"
```

### Panic Fix Detection

Find commits that indicate urgent bug fixes:
```bash
curl "http://localhost:8000/api/snowflake/analytics/panic-fixes?repo_name=myrepo&days=30"
```

### AI-Powered Analysis with Cortex

Use Cortex to analyze any text:
```bash
curl -X POST http://localhost:8000/api/snowflake/cortex/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze this git diff and explain what bug was fixed: [diff here]",
    "model": "mistral-large"
  }'
```

---

## 📊 Comparison: Elasticsearch vs Snowflake

| Feature | Elasticsearch | Snowflake + Cortex |
|---------|--------------|-------------------|
| Search | Keyword + fuzzy | Semantic (understands meaning) |
| AI Functions | ❌ None | ✅ COMPLETE, SENTIMENT, SUMMARIZE, EXTRACT |
| Data Warehouse | ❌ No | ✅ Yes (analytics, aggregations) |
| Time Travel | ❌ No | ✅ Query historical states |
| Cost | $$$ (always running) | $ (pay per query, auto-suspend) |
| Setup Complexity | Medium | Low (managed service) |
| ML/AI Integration | Manual | Built-in Cortex |

**Recommendation:** Use Snowflake for:
- Semantic search (better than Elasticsearch keyword matching)
- Analytics and reporting
- Long-term data storage
- AI-powered analysis

---

## 🐛 Troubleshooting

### Error: "Snowflake is not connected"
- Check `ENABLE_SNOWFLAKE=true` in `.env`
- Verify credentials are correct
- Run: `pip install snowflake-connector-python`

### Error: "Cortex functions not available"
- Requires Snowflake **Enterprise** edition
- Set `ENABLE_CORTEX_LLM=true` in `.env`
- Check trial includes Enterprise features

### Error: "Table does not exist"
- Run SQL setup from `SNOWFLAKE_INTEGRATION.md`
- Check you're in the correct database/schema:
  ```sql
  USE DATABASE BUGREWIND;
  USE SCHEMA GIT_ANALYSIS;
  SHOW TABLES;
  ```

### Error: "COMMIT_SEARCH does not exist"
- Create Cortex Search service (see `SNOWFLAKE_INTEGRATION.md`)
- This requires Enterprise edition

---

## 📈 Next Steps

Now that Snowflake is integrated, you can:

1. **Migrate from Elasticsearch** - Replace Elastic calls with Snowflake
2. **Enhance Bug Analysis** - Store all analysis results in Snowflake for analytics
3. **Build Dashboard** - Create analytics dashboard using Snowflake data
4. **Update Postman Flow** - Use Snowflake endpoints in your flow
5. **Add Real-time Ingestion** - Use Snowpipe for continuous commit indexing

---

## 🎯 Demo for Hackathon

**Killer Features to Show:**

1. **Semantic Search:** "Show me commits related to authentication security issues"
   - Better than keyword search
   - Understands intent

2. **Panic Fix Detection:** Automatically find urgent bug fixes using sentiment
   - Shows which areas of code are problematic
   - Predicts future bugs

3. **Time Travel:** Query how the codebase looked at any point in time
   - "What did the auth code look like before the bug?"

4. **AI Analysis:** Use Cortex to explain what commits do
   - No need for external LLM APIs
   - Built into the data warehouse

---

**Questions? Check `SNOWFLAKE_INTEGRATION.md` for complete documentation!**
