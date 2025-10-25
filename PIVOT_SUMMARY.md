# Project Pivot: Bug Archaeology → PM Copilot with Receipts

**Date:** 2025-10-25
**Status:** Architecture complete, ready to update Phase 1

---

## 📊 What Changed

### **Before: Bug Archaeology**
- Find when/where bugs were introduced
- Trace git history for bug origins
- OCR error screenshots
- Manual analysis workflow

**Problem:** Cool tech demo, but narrow use case. Judges ask "who actually uses this?"

### **After: PM Copilot with Receipts**
- PM speaks vague spec → get receipts, impact, patch, PR, task
- Multi-API orchestration (Slack → Postman → Elastic → Claude → GitHub/Asana)
- Audit trail for every decision (commit quotes, co-change scores, ownership)
- Closes the loop from intent → shipped code

**Why Better:** Solves the "95% of GenAI pilots fail" problem (integration + workflow). Judges can click the Postman Action URL and see the full reasoning chain.

---

## 🏗️ New Architecture at a Glance

```
Slack /impact command
    ↓
Postman Flow (deployed Action URL)
    ↓
Elasticsearch (hybrid search: BM25 + kNN embeddings)
    ↓
ES|QL + Graph (co-change analysis, ownership, risk)
    ↓
Claude API (≤30-line patch + test)
    ↓
GitHub PR + Asana task
    ↓
Slack Block Kit summary (receipts + links)
```

**Judge-clickable artifacts:**
1. Postman Action URL (shows orchestration)
2. Elastic Graph Explore (visual impact map)
3. GitHub PR (auto-created with receipts)
4. Slack Block Kit (final UX)

---

## 🔄 What Stays the Same (Reusable from Phase 1)

✅ **Elasticsearch Serverless** - same setup process
✅ **Git commit extraction** - `app/git/analyzer.py` still works
✅ **Bulk indexing** - `app/elastic/indexer.py` still works
✅ **Test infrastructure** - test_phase1.py pattern reusable

**Key insight:** ~60% of Phase 1 code is still valid!

---

## 🆕 What's New (Additions to Phase 1)

### 1. **Vector Embeddings**
- Add `message_embedding` field (dense_vector, 384-dim)
- Integrate OpenAI/Cohere embedding API
- Embed commit messages during indexing

**Code impact:**
- New file: `app/embeddings/client.py`
- Update: `app/elastic/schema.py` (add dense_vector field)
- Update: `app/git/analyzer.py` (call embedding API)

### 2. **Hybrid Search (RRF)**
- Replace simple text search with BM25 + kNN
- Use Elasticsearch Retrievers framework
- Return ranked results from both methods

**Code impact:**
- New file: `app/elastic/search.py` (query builders)
- Update: `test_phase1.py` (test hybrid queries)

### 3. **Files Index + Co-Change**
- New index for file-level metadata
- Compute co-change scores (files that change together)
- Track code ownership (top contributors per file)

**Code impact:**
- New file: `app/elastic/files_indexer.py`
- New file: `app/analytics/co_change.py`

---

## 📋 Updated Phase 1 Scope

### **Old Phase 1:** Elasticsearch Setup & Basic Indexing
- Connect to Elastic
- Create `commits` index
- Index commit metadata
- Basic text search

### **New Phase 1:** Elasticsearch + Vector Search Setup
- Connect to Elastic ✓ (same)
- Create `commits` index with **embeddings** (new)
- Integrate **embedding API** (new)
- Index commits with **text + vectors** (updated)
- Test **hybrid search** (new)

**Time:** 5-6 hours (was 4-5 hours)

---

## 🛠️ Action Items to Update Phase 1

### 1. **Update Schema** (`app/elastic/schema.py`)
Add to `COMMIT_INDEX_MAPPING`:
```python
"message_embedding": {
    "type": "dense_vector",
    "dims": 384,
    "similarity": "dot_product",
    "index": True,
    "index_options": {
        "type": "int8_hnsw",
        "m": 16,
        "ef_construction": 100
    }
}
```

### 2. **Create Embedding Client** (`app/embeddings/client.py`)
```python
class EmbeddingClient:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Call OpenAI API
        # Return 384-dim vectors
        pass
```

### 3. **Update Git Analyzer** (`app/git/analyzer.py`)
Add embedding call to `extract_commit_data()`:
```python
# After extracting message
embedding = embedding_client.embed([commit.message])[0]
commit_data['message_embedding'] = embedding
```

### 4. **Create Search Module** (`app/elastic/search.py`)
```python
def hybrid_search(query_text: str, query_vector: List[float], repo_id: str):
    # Build RRF retriever query
    # Combine BM25 + kNN
    # Return ranked results
    pass
```

### 5. **Update Test Script** (`test_phase1.py`)
Add hybrid search test:
```python
def test_hybrid_search():
    # Embed query text
    # Run hybrid search
    # Verify results contain both BM25 and kNN matches
    pass
```

### 6. **Update Environment** (`.env.example`)
Add:
```env
OPENAI_API_KEY=your_openai_key_here
EMBEDDING_MODEL=text-embedding-3-small
```

### 7. **Update Dependencies** (`requirements.txt`)
Add:
```
openai==1.12.0
```

---

## 🎯 Phases 2-5 Summary (New Scope)

### **Phase 2: Impact Set Analysis** (4-5 hours)
- Create `files` index
- ES|QL co-change queries
- Code ownership tracking
- Graph Explore visual map

### **Phase 3: Postman Flow Orchestration** (5-6 hours)
- Build Postman collection
- Create Flow with AI Agent block
- Connect all APIs (Elastic, Claude, GitHub)
- Deploy as Action URL

### **Phase 4: Claude Integration + PR Creation** (4-5 hours)
- Claude Messages API for patch generation
- GitHub PR creation (REST API)
- Asana task creation
- Test end-to-end

### **Phase 5: Slack Integration + Risk Scoring** (4-5 hours)
- Slack slash command (`/impact`)
- HMAC signature verification
- Block Kit UI
- Risk scoring (flake density, churn)
- App Home (optional)

**Total:** ~22-27 hours (matches original DEV_B estimate)

---

## 🚀 Why This Pivot Is Smart

### 1. **Addresses "Why GenAI Fails" Problem**
> 95% of GenAI pilots fail due to *integration and workflow* issues, not model IQ.

Your system **is** the integration layer. It connects:
- Slack (PM's actual workflow)
- Postman (orchestration brain)
- Elastic (data + receipts)
- Claude (intelligence)
- GitHub/Asana (execution)

### 2. **Multi-Sponsor Prize Alignment**
- **Postman:** AI Agent orchestration + deployed Action URL
- **Elastic:** Hybrid search + Graph + MCP server (Agent Builder)
- **Claude:** Patch generation via Messages API
- **MLH:** .tech domain, DO hosting for dashboard

### 3. **Judge-Clickable Artifacts**
Every piece is **verifiable**:
- Action URL → shows reasoning chain
- Graph Explore → visual proof of impact
- PR → auto-created with receipts
- Slack → final UX demo

### 4. **Differentiated**
Not "chat over issues" (saturated space). This is:
- **Receipts-first** (every decision cited)
- **Action-oriented** (creates PR + task)
- **Audit-friendly** (judges can verify logic)

### 5. **Realistic Scope**
- 5 phases, ~5 hours each = 25 hours
- Clear deliverables per phase
- Each phase is demo-able (incremental progress)

---

## 🎬 Demo Script (30 seconds)

1. **Open Slack:** "Here's a PM who has a vague idea"
2. **Type:** `/impact "Add ProfileCard to /users; keep snapshot stable"`
3. **Wait 10s:** Bot replies "working..."
4. **Show Block Kit:**
   - Acceptance criteria (auto-generated)
   - Impact set: `[UserProfile.tsx, ProfileCard.test.ts, ...]`
   - Receipts: Commit quotes showing why these files matter
   - Risk score: 35/100 (medium)
   - Buttons: "Open PR" | "View Graph"
5. **Click "Open PR":** GitHub PR is already created with ≤30-line patch
6. **Click "View Graph":** Elastic Graph shows co-change network
7. **End:** "From vague spec to shippable PR in 10 seconds, with full receipts."

**Judge reaction:** "How did you connect all these APIs?" → "Postman Flow deployed as an Action URL. Here's the artifact."

---

## ⚠️ Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Embeddings cost money** | Use small model (`text-embedding-3-small` = $0.02/1M tokens), batch requests, cache embeddings |
| **Hybrid search complexity** | Start with RRF (no tuning), benchmark against BM25-only |
| **Postman Flow learning curve** | Build incrementally: start with single HTTP block, add AI Agent last |
| **Slack slash command flakes** | Always ack <3s, use `response_url` for delayed reply, verify HMAC |
| **Over-scope** | Enforce ≤30-line patch rule, skip OCR (not needed for MVP) |

---

## ✅ Ready to Proceed?

**Current Status:**
- ✅ Architecture designed (`ARCHITECTURE.md`)
- ✅ 5-phase plan updated
- ✅ Reusable code identified (60% of Phase 1)
- ✅ New components scoped (embeddings, hybrid search)
- ⏳ Waiting to update Phase 1 code

**Next Steps:**
1. **Update Phase 1 code** (5-6 hours):
   - Add embedding client
   - Update schema with dense_vector
   - Integrate OpenAI API
   - Test hybrid search
2. **Test with real repo** (include embeddings)
3. **Commit Phase 1 (updated)**
4. **Proceed to Phase 2** (impact set analysis)

---

## 🎓 Key Takeaways

| Metric | Old (Bug Archaeology) | New (PM Copilot) |
|--------|----------------------|------------------|
| **Use case** | Narrow (debug only) | Broad (every PM spec) |
| **Integration** | Standalone tool | Multi-API orchestration |
| **Output** | Analysis report | PR + task + receipts |
| **Differentiation** | "Better git blame" | "Receipts-first AI workflow" |
| **Judge appeal** | "Cool tech" | "Solves real problem + shows integration" |
| **Prize alignment** | Claude only | Postman + Elastic + Claude + MLH |

**Verdict:** The pivot is a **significant upgrade** in scope, differentiation, and judge appeal.

---

**Ready to update Phase 1 code?** Let me know and I'll:
1. Add embedding client (`app/embeddings/client.py`)
2. Update schema with vectors
3. Integrate OpenAI API into git analyzer
4. Add hybrid search queries
5. Update test script
6. Provide new PHASE1_README

Just say "yes" and I'll proceed! 🚀
