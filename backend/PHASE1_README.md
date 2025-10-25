# Phase 1: Elasticsearch Setup & Basic Indexing

**Status:** Ready to test
**Duration:** 4-5 hours
**Goal:** Set up Elastic Serverless and verify basic commit indexing

## 📋 Prerequisites

1. **Elasticsearch Serverless Account**
   - Go to https://cloud.elastic.co/
   - Create account or sign in
   - Create a new "Serverless Project" (Elasticsearch type)
   - Note the endpoint URL (looks like: `https://your-project.es.region.gcp.cloud.es.io`)

2. **API Key Generation**
   - In Elastic Console, go to: Stack Management → API Keys
   - Click "Create API Key"
   - Give it a name (e.g., "BugRewind Dev")
   - Copy the encoded API key (you won't see it again!)

3. **Python Environment**
   ```bash
   cd backend
   source venv/bin/activate  # Or: venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. **Create `.env` file** in `backend/` directory:
   ```bash
   cp .env.example .env
   ```

2. **Add your Elastic credentials** to `backend/.env`:
   ```env
   # Required for Phase 1
   ELASTIC_API_KEY=your_api_key_here
   ELASTIC_ENDPOINT=https://your-project.es.region.gcp.cloud.es.io

   # Optional for Phase 1 (can leave defaults)
   PORT=8000
   CLONE_DIR=/tmp/bugrewind-clones
   ```

## 🧪 Running the Tests

From the `backend/` directory:

```bash
python test_phase1.py
```

### What the test does:
1. ✅ **Connection Test** - Verifies Elastic credentials
2. ✅ **Index Creation** - Creates `commits` index with schema
3. ✅ **Repository Clone** - Clones a small test repo (BentoML)
4. ✅ **Commit Extraction** - Extracts 50 commits with metadata
5. ✅ **Bulk Indexing** - Indexes commits into Elasticsearch
6. ✅ **Search Verification** - Runs 3 test queries

**Expected output:**
```
╔════════════════════════════════════════════════════════╗
║               PHASE 1 TEST SUITE                       ║
║          Elasticsearch Setup & Basic Indexing          ║
╚════════════════════════════════════════════════════════╝

TEST 1: Elasticsearch Connection
==========================================================
Connecting to: https://...
✅ Elasticsearch connection successful!

TEST 2: Index Creation
==========================================================
✅ Index 'commits' created successfully!

TEST 3-5: Repository Indexing
==========================================================
✅ Repository cloned successfully!
✅ Extracted 50 commits
✅ Indexed 50 commits

TEST 6: Basic Search Queries
==========================================================
✅ Found 50 total commits
...

🎉 Phase 1 Complete! All tests passed.
```

## 🏗️ What Was Built

### File Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── elastic/
│   │   ├── __init__.py
│   │   ├── client.py          # Elasticsearch connection
│   │   ├── schema.py          # Index mapping definition
│   │   └── indexer.py         # Indexing logic
│   └── git/
│       ├── __init__.py
│       └── analyzer.py        # Git commit extraction
├── test_phase1.py             # Phase 1 test suite
├── PHASE1_README.md           # This file
└── .env                       # Your credentials (not committed)
```

### Key Components

**`app/config.py`**
- Loads environment variables
- Validates required configuration
- Central config management

**`app/elastic/client.py`**
- Elasticsearch connection wrapper
- Connection pooling and error handling
- Ping test for health checks

**`app/elastic/schema.py`**
- Commit index mapping optimized for search
- Fields for git metadata, file changes, diffs
- Nested structure for file changes array

**`app/elastic/indexer.py`**
- Create/delete index operations
- Single and bulk commit indexing
- Index statistics and refresh

**`app/git/analyzer.py`**
- Clone GitHub repositories
- Extract structured commit data
- Parse diffs for file changes and stats
- Cleanup temporary clones

## 🔍 Verify in Elastic Console

After successful test, verify in Elastic Console:

1. **Go to Dev Tools** (Console)
2. **Check index exists:**
   ```json
   GET /commits
   ```

3. **Count documents:**
   ```json
   GET /commits/_count
   ```

4. **View sample commit:**
   ```json
   GET /commits/_search
   {
     "size": 1,
     "sort": [{"commit_date": "desc"}]
   }
   ```

5. **Search by author:**
   ```json
   GET /commits/_search
   {
     "query": {
       "match": {"author_name": "replace_with_author"}
     }
   }
   ```

## 🐛 Troubleshooting

### "Connection failed"
- Check `ELASTIC_ENDPOINT` - should start with `https://`
- Verify API key is correct (no spaces/newlines)
- Check network/firewall settings

### "Authentication failed"
- Regenerate API key in Elastic Console
- Make sure you copied the full encoded key
- Check for trailing spaces in `.env`

### "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### "Repository clone failed"
- Check network connection
- Verify GitHub access (repo might be private)
- Try a different test repo in `test_phase1.py`

## ✅ Phase 1 Complete Checklist

- [ ] Elastic Serverless project created
- [ ] API key generated and added to `.env`
- [ ] All tests pass (`python test_phase1.py`)
- [ ] Can view indexed commits in Elastic Console
- [ ] Search queries return results
- [ ] Ready to commit code

## 📤 Commit This Phase

Once all tests pass:

```bash
git add backend/app backend/test_phase1.py backend/PHASE1_README.md
git commit -m "Phase 1: Elasticsearch setup and basic commit indexing

- Added Elastic client connection with health checks
- Defined commit index schema optimized for git archaeology
- Built commit indexer with bulk operations
- Created git analyzer for repository cloning and commit extraction
- Implemented Phase 1 test suite (6 tests)
- Successfully indexed 50 commits from test repository
- Verified search functionality with multiple query types"
```

## 🚀 Next: Phase 2

Phase 2 will focus on:
- Search query optimization
- Relevance scoring for bug-related searches
- Performance testing with larger repositories
- Advanced query patterns (file path search, date ranges, etc.)
