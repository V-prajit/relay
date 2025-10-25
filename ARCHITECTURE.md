# PM Copilot Architecture: Vague Specs → Receipts → Impact → Tiny PR

**System Goal:** Transform vague PM descriptions into actionable PRs with full audit trails

---

## 🎯 End-to-End Flow

```
Slack: /impact "Add ProfileCard to /users"
    ↓
Postman Flow (deployed Action URL)
    ↓ (embeds PM text)
Elasticsearch Hybrid Search
    ↓ (finds relevant commits/files)
Elastic Graph + ES|QL
    ↓ (computes impact set with receipts)
Claude API
    ↓ (drafts ≤30-line patch + test)
GitHub PR + Asana Task
    ↓
Slack Block Kit Summary
    → Intent, acceptance criteria, impact, risk, commit quotes, PR/task links
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SLACK (PM Front-Door)                 │
│  • /impact slash command (3s ack, delayed reply)            │
│  • Block Kit results UI                                      │
│  • App Home for open items                                   │
└────────────────────┬────────────────────────────────────────┘
                     │ webhook POST (verified HMAC)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              POSTMAN FLOW (deployed as Action URL)           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. AI Agent Block: Parse PM intent                  │    │
│  │    → Extract entities, generate acceptance criteria │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 2. HTTP: Call Embedding API (OpenAI/Cohere)        │    │
│  │    → Get 384-dim vector from PM description         │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 3. HTTP: Elasticsearch Hybrid Search (RRF)         │    │
│  │    → BM25 + kNN retriever for relevant commits      │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 4. HTTP: Elastic ES|QL + Graph Explore             │    │
│  │    → Compute impact set, co-change scores, owners   │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 5. HTTP: Claude Messages API                        │    │
│  │    → Generate ≤30-line patch + snapshot test        │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 6. HTTP: GitHub Create PR + Asana Create Task      │    │
│  │    → Push work forward, attach receipts JSON        │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 7. HTTP: Slack response_url (delayed reply)        │    │
│  │    → Post Block Kit summary with links              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  ELASTICSEARCH SERVERLESS                    │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  commits index   │  │   files index    │                 │
│  │  • Hybrid search │  │  • Owners        │                 │
│  │  • ELSER + kNN   │  │  • Test deps     │                 │
│  │  • Embeddings    │  │  • Co-change map │                 │
│  └──────────────────┘  └──────────────────┘                 │
│  ┌──────────────────────────────────────────┐               │
│  │  Graph API: Co-change network            │               │
│  │  → Visual map of impact (judge-clickable)│               │
│  └──────────────────────────────────────────┘               │
│  ┌──────────────────────────────────────────┐               │
│  │  Agent Builder + MCP Server              │               │
│  │  → Expose ES|QL queries as tools         │               │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Elasticsearch Index Schemas

### 1. **commits** Index (Primary Search Target)

```json
{
  "mappings": {
    "properties": {
      "commit_hash": {"type": "keyword"},
      "repo_id": {"type": "keyword"},
      "timestamp": {"type": "date"},
      "author": {"type": "keyword"},
      "author_name": {
        "type": "text",
        "fields": {"keyword": {"type": "keyword"}}
      },

      "message": {
        "type": "text",
        "fields": {
          "elser": {"type": "sparse_vector"}
        }
      },
      "message_embedding": {
        "type": "dense_vector",
        "dims": 384,
        "similarity": "dot_product",
        "index": true,
        "index_options": {"type": "int8_hnsw"}
      },

      "files_changed": {"type": "keyword"},

      "diffs": {
        "type": "nested",
        "properties": {
          "file_path": {"type": "keyword"},
          "change_type": {"type": "keyword"},
          "hunk": {"type": "text", "index": false},
          "hunk_embedding": {
            "type": "dense_vector",
            "dims": 384,
            "index": true,
            "index_options": {"type": "int8_hnsw"}
          },
          "lines_added": {"type": "integer"},
          "lines_removed": {"type": "integer"}
        }
      },

      "total_additions": {"type": "integer"},
      "total_deletions": {"type": "integer"},
      "test_files_touched": {"type": "keyword"},
      "is_flaky_fix": {"type": "boolean"},
      "indexed_at": {"type": "date"}
    }
  },
  "settings": {
    "number_of_shards": 1,
    "index": {
      "max_result_window": 10000
    }
  }
}
```

### 2. **files** Index (Impact Set & Ownership)

```json
{
  "mappings": {
    "properties": {
      "file_path": {"type": "keyword"},
      "repo_id": {"type": "keyword"},
      "extension": {"type": "keyword"},
      "is_test_file": {"type": "boolean"},

      "owners": {
        "type": "nested",
        "properties": {
          "author": {"type": "keyword"},
          "commit_count": {"type": "integer"},
          "last_touched": {"type": "date"}
        }
      },

      "co_change_scores": {
        "type": "object",
        "enabled": false
      },

      "test_dependencies": {"type": "keyword"},
      "flake_density": {"type": "float"},
      "recent_churn": {"type": "integer"},
      "risk_score": {"type": "float"}
    }
  }
}
```

### 3. **test_runs** Index (Flake Detection)

```json
{
  "mappings": {
    "properties": {
      "test_file": {"type": "keyword"},
      "test_name": {"type": "keyword"},
      "status": {"type": "keyword"},
      "run_timestamp": {"type": "date"},
      "commit_hash": {"type": "keyword"},
      "files_under_test": {"type": "keyword"}
    }
  }
}
```

---

## 🔍 Key Query Patterns

### Query 1: Hybrid Search for PM Description

```json
POST /commits/_search
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "standard": {
            "query": {
              "multi_match": {
                "query": "{{pm_description}}",
                "fields": ["message^2", "files_changed", "author_name"]
              }
            }
          }
        },
        {
          "knn": {
            "field": "message_embedding",
            "query_vector": [...],  // 384-dim from embedding API
            "k": 50,
            "num_candidates": 200,
            "filter": {
              "bool": {
                "must": [
                  {"term": {"repo_id": "{{repo}}"}},
                  {"range": {"timestamp": {"gte": "now-6M"}}}
                ]
              }
            }
          }
        }
      ],
      "rank_window_size": 100
    }
  },
  "aggs": {
    "impacted_files": {
      "terms": {"field": "files_changed", "size": 50}
    },
    "top_authors": {
      "terms": {"field": "author", "size": 10}
    }
  },
  "size": 20
}
```

### Query 2: Co-Change Analysis (ES|QL)

```sql
FROM commits
| WHERE repo_id == "{{repo}}" AND timestamp > NOW() - 6 MONTHS
| STATS commit_count = COUNT(*) BY files_changed
| WHERE commit_count > 1
| LIMIT 1000
```

Then compute pairwise co-change scores (client-side or pre-indexed).

### Query 3: Graph Explore for Impact Map

```json
POST /commits/_graph/explore
{
  "controls": {
    "use_significance": true,
    "sample_size": 1000
  },
  "query": {
    "terms": {"files_changed": ["src/auth/login.py"]}
  },
  "vertices": [
    {"field": "files_changed", "size": 20}
  ],
  "connections": {
    "vertices": [
      {"field": "files_changed"}
    ]
  }
}
```

Returns graph of files that co-change with `login.py` (judge-clickable visual).

---

## 🧠 Vector Embedding Strategy

### What Gets Embedded?

1. **Commit Messages** → `message_embedding` (384-dim)
   - Model: `all-MiniLM-L6-v2` or ELSER
   - Chunking: None (messages are short)

2. **Diff Hunks** → `diffs[].hunk_embedding` (384-dim)
   - Model: Same as messages
   - Chunking: By hunk (±3 context lines)
   - Purpose: Find similar code changes

3. **PM Descriptions** → Query vector (384-dim)
   - Embedded at query time via Postman Flow
   - API: OpenAI `text-embedding-3-small` or Cohere `embed-v3`

### Embedding Pipeline

```
Ingest Commit → Extract message + diffs
    ↓
Call Embedding API (batch 100 messages)
    ↓
Store embeddings in `commits` index
    ↓
(Repeat for diff hunks if needed)
```

**Note:** For Phase 1, embed **only commit messages**. Diff embeddings are Phase 5 (advanced).

---

## 🛠️ Updated 5-Phase Implementation Plan

### **Phase 1: Elasticsearch + Vector Search Setup** (5-6 hours)

**Goal:** Get Elastic indexing commits with hybrid search (BM25 + kNN)

**Tasks:**
1. Set up Elasticsearch Serverless (same as before)
2. Define `commits` index with:
   - `message_embedding` (dense_vector, 384-dim, int8_hnsw)
   - `message` with ELSER field (sparse_vector)
   - Basic metadata (SHA, author, files_changed)
3. Integrate embedding API (OpenAI or Cohere):
   - Add `OPENAI_API_KEY` to `.env`
   - Create `app/embeddings/client.py` for batch embedding
4. Update Git analyzer to:
   - Extract commit message
   - Call embedding API
   - Index with both text + vector
5. Test hybrid search (RRF retriever):
   - Query: "authentication bug"
   - Verify both BM25 and kNN results

**Deliverables:**
- `commits` index with embeddings
- Hybrid search working
- Test script with sample queries

**Commit:** "Phase 1: Elasticsearch hybrid search with embeddings"

---

### **Phase 2: Impact Set Analysis (Co-Change + Ownership)** (4-5 hours)

**Goal:** Compute "files that change together" and code ownership

**Tasks:**
1. Create `files` index schema
2. Build ES|QL queries for:
   - Co-change frequency (files appearing in same commits)
   - Code ownership (top-3 contributors per file)
3. Pre-compute co-change scores during indexing:
   - For each commit, update pairwise file scores
   - Store in `files.co_change_scores` object
4. Build Graph Explore query for visual impact map
5. Create REST endpoint (or Postman Flow block) to:
   - Accept file path
   - Return impact set (files with co-change > 0.6)
   - Return owners + recent churn

**Deliverables:**
- `files` index populated
- Co-change graph working
- Graph Explore visual (screenshot for demo)

**Commit:** "Phase 2: Impact set analysis with co-change and ownership"

---

### **Phase 3: Postman Flow Orchestration** (5-6 hours)

**Goal:** Build the brain that connects all APIs

**Tasks:**
1. Create Postman collection with:
   - Elastic hybrid search request
   - Elastic ES|QL co-change query
   - Elastic Graph Explore
   - Embedding API call (OpenAI)
   - Claude Messages API (for patch)
2. Build Postman Flow:
   - Input: `{pm_description, repo_id}`
   - Block 1: AI Agent parses intent
   - Block 2: Call embedding API
   - Block 3: Hybrid search on Elastic
   - Block 4: ES|QL for impact set
   - Block 5: Format receipts JSON
3. Deploy Flow as Postman Action:
   - Get public Action URL
   - Test with curl/Postman
4. Document request/response format

**Deliverables:**
- Postman Flow working end-to-end
- Deployed Action URL
- Sample receipts JSON output

**Commit:** "Phase 3: Postman Flow orchestration with Action URL"

---

### **Phase 4: Claude Integration + PR Creation** (4-5 hours)

**Goal:** Generate patch + test, create GitHub PR + Asana task

**Tasks:**
1. Add Claude Messages API call to Postman Flow:
   - Input: PM description + impact set + commit receipts
   - Prompt: "Generate ≤30-line patch + snapshot test"
   - Parse response for code blocks
2. Add GitHub PR creation:
   - Create branch via REST API
   - Commit patch
   - Open PR with receipts in description
3. Add Asana task creation:
   - POST /tasks with acceptance criteria
   - Link to PR and Slack message
4. Test end-to-end:
   - PM description → patch → PR → task

**Deliverables:**
- Claude generating patches
- GitHub PR auto-created
- Asana task linked

**Commit:** "Phase 4: Claude patch generation with PR and task creation"

---

### **Phase 5: Slack Integration + Risk Scoring** (4-5 hours)

**Goal:** Production-ready PM interface with risk metrics

**Tasks:**
1. Create Slack app:
   - Slash command `/impact`
   - Verify HMAC signatures
   - 3s ack + delayed reply via `response_url`
2. Build Block Kit template:
   - Acceptance criteria
   - Impact set (files + owners)
   - Commit receipts (quotes + links)
   - Risk score (flake density + churn)
   - Buttons: "Open PR", "View Graph"
3. Add risk scoring:
   - Ingest test run history → `test_runs` index
   - Compute flake density per file
   - Weight by recent churn (commits in last 30d)
   - Return risk score (0-100)
4. Optional: App Home for open items
5. Polish demo flow

**Deliverables:**
- Slack slash command working
- Block Kit UI polished
- Risk scores displayed
- Full demo video

**Commit:** "Phase 5: Slack integration with risk scoring and Block Kit UI"

---

## 🎯 Data Ingestion Pipeline

```
GitHub Repo
    ↓
1. Clone repo (GitPython)
    ↓
2. Extract commits (SHA, message, author, files_changed, diffs)
    ↓
3. Call Embedding API (batch 100 messages)
    → Returns 384-dim vectors
    ↓
4. Index into Elastic `commits` (bulk API)
    ↓
5. Aggregate file statistics
    → Co-change scores (pairwise)
    → Ownership (top-3 authors per file)
    → Test dependencies (test files in same commits)
    ↓
6. Index into Elastic `files`
    ↓
7. (Optional) Ingest test run history → `test_runs`
```

**Performance:**
- 1000 commits = ~10s git extraction + ~5s embedding (batch) + ~2s indexing = **~17s total**
- Use `elasticsearch.helpers.bulk()` for indexing

---

## 🔑 Environment Variables (Updated)

```env
# Elasticsearch
ELASTIC_API_KEY=your_elastic_key
ELASTIC_ENDPOINT=https://your-project.es...

# Embeddings (choose one)
OPENAI_API_KEY=your_openai_key       # For text-embedding-3-small
COHERE_API_KEY=your_cohere_key       # Alternative

# Claude
CLAUDE_API_KEY=your_claude_key

# GitHub
GITHUB_TOKEN=your_github_pat

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...

# Asana
ASANA_ACCESS_TOKEN=...

# Optional
DEEPSEEK_API_KEY=...                 # For OCR (future)
```

---

## 🎓 Why This Architecture Wins

1. **Receipts = Trust**
   - Every decision backed by commit quotes, co-change scores, ownership data
   - Graph Explore is judge-clickable visual proof

2. **Hybrid Search = Best of Both Worlds**
   - BM25 catches exact matches (file names, author names)
   - kNN catches semantic intent ("authentication issues")
   - RRF combines without tuning

3. **Small PRs = Reviewable**
   - ≤30-line rule keeps patches focused
   - Snapshot tests auto-generated
   - Reduces merge hell

4. **Postman Action = Transparent**
   - Deployed URL is the artifact judges can click
   - Logs show full reasoning chain
   - JSON receipts are machine-readable

5. **Multi-API Orchestration**
   - Exactly what Postman/Elastic/Claude judges want to see
   - Not just "chat over issues" — closes the loop

---

## 📊 Success Metrics

- **Hybrid search recall:** >95% for relevant commits
- **Impact set accuracy:** >80% co-change prediction
- **Patch size:** <30 lines (enforced)
- **E2E latency:** <30s from Slack → PR created
- **Risk score precision:** Correlates with actual flakes

---

## 🚀 Next Steps

1. **Update Phase 1** to include:
   - Embedding API integration
   - Hybrid search (RRF)
   - Vector field in schema

2. **Test embedding pipeline** with small repo

3. **Proceed with Phases 2-5** as outlined

Let me know when you're ready to update Phase 1 code!
