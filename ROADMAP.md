# Relay Roadmap

Planned features and architectural improvements for future development.

---

## Overview

This document outlines unimplemented features and architectural enhancements that would significantly improve Relay's capabilities. These features are designed to address scalability, accuracy, and intelligence limitations in the current implementation.

---

## Table of Contents

1. [Elasticsearch Vector Search](#elasticsearch-vector-search)
2. [DeepSeek OCR Integration](#deepseek-ocr-integration)
3. [Conflict Detection and Co-Change Analysis](#conflict-detection-and-co-change-analysis)
4. [Analytics Dashboard](#analytics-dashboard)
5. [CI/CD Integration](#cicd-integration)
6. [Multi-Repository Support](#multi-repository-support)

---

## Elasticsearch Vector Search

### Problem Statement

The current implementation uses ripgrep for code search, which performs literal string matching and regex pattern matching. This approach has limitations:

- **No semantic understanding**: Cannot find conceptually related code without exact keyword matches
- **Limited context**: Searches individual lines without understanding code structure
- **Poor scalability**: Performance degrades with repository size
- **No similarity ranking**: All matches are treated equally

### Proposed Solution

Replace ripgrep with Elasticsearch using vector embeddings for semantic code search.

### Architecture

```
Feature Request
    ↓
Generate Query Embedding (OpenAI/Cohere)
    ↓
Elasticsearch Vector Search (k-NN)
    ↓
Retrieve Top-K Similar Code Blocks
    ↓
Re-rank by Relevance
    ↓
Return Impacted Files
```

### Technical Implementation

**1. Index Code at Build Time**:

```python
from elasticsearch import Elasticsearch
from openai import OpenAI

# Generate embeddings for code blocks
def index_codebase(repo_path):
    es = Elasticsearch("https://elastic-instance:9200")
    openai = OpenAI(api_key="...")

    for file_path in walk_codebase(repo_path):
        code_blocks = extract_functions_and_classes(file_path)

        for block in code_blocks:
            # Generate embedding
            embedding = openai.embeddings.create(
                model="text-embedding-3-small",
                input=block.code
            ).data[0].embedding

            # Index in Elasticsearch
            es.index(index="codebase", document={
                "file_path": file_path,
                "code": block.code,
                "type": block.type,  # function, class, method
                "name": block.name,
                "embedding": embedding,
                "language": "typescript"
            })
```

**2. Query at Runtime**:

```python
def search_code(query_text: str, top_k: int = 10):
    # Generate query embedding
    query_embedding = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    ).data[0].embedding

    # Search Elasticsearch
    results = es.search(index="codebase", body={
        "knn": {
            "field": "embedding",
            "query_vector": query_embedding,
            "k": top_k,
            "num_candidates": 100
        },
        "_source": ["file_path", "code", "name", "type"]
    })

    return [
        {
            "file": hit["_source"]["file_path"],
            "relevance_score": hit["_score"],
            "code_snippet": hit["_source"]["code"]
        }
        for hit in results["hits"]["hits"]
    ]
```

**3. Integration with Postman Flow**:

Replace the Ripgrep API HTTP Request block with an Elasticsearch API call. The response format remains compatible with existing workflow.

### Benefits

- **Semantic search**: Find related code even without exact keywords
- **Better ranking**: Relevance scores prioritize most impacted files
- **Scalability**: Elasticsearch handles massive codebases efficiently
- **Rich queries**: Combine vector search with filters (file type, language, last modified)

### Technical Requirements

**Infrastructure**:
- Elasticsearch cluster (Elastic Cloud or self-hosted)
- Embedding API (OpenAI, Cohere, or open-source model)
- Indexing pipeline (GitHub Actions on push events)

**Estimated Costs** (for 10K code files):
- Elasticsearch: ~$45/month (Elastic Cloud)
- OpenAI embeddings: ~$0.10 per million tokens (one-time indexing + incremental updates)
- Total: ~$50/month

### Implementation Priority

**Phase 1** (MVP):
- Index entire codebase with function-level granularity
- Implement basic k-NN search
- Integrate with existing Postman Flow

**Phase 2** (Enhanced):
- Add hybrid search (combine vector + keyword matching)
- Implement incremental indexing (only changed files)
- Add language-specific parsers for better code understanding

**Phase 3** (Advanced):
- Multi-repository search
- Dependency graph integration
- Historical code pattern analysis

---

## DeepSeek OCR Integration

### Problem Statement

Large codebases exceed LLM context windows, making it difficult to provide comprehensive context for issue generation. Current limitations:

- **Context window limits**: Most LLMs support 8K-128K tokens
- **Token costs**: Large context windows are expensive ($10-50 per million tokens)
- **Incomplete context**: Cannot include full codebase, leading to incomplete analysis

### Proposed Solution

Use DeepSeek OCR technology to compress code into visual tokens, achieving 10x context compression with 97% precision.

### How DeepSeek OCR Works

**Traditional Approach**:
```
Code (10,000 lines) → Tokenize → 50,000 tokens → Exceeds context limit
```

**DeepSeek OCR Approach**:
```
Code (10,000 lines) → Render as image → OCR compression → 5,000 visual tokens → Fits in context
```

**Key Insight**: Visual tokens can represent more information per token than text tokens, enabling 10:1 compression ratio while maintaining 97% OCR precision.

### Architecture

```
Feature Request + Impacted Files (from Elasticsearch)
    ↓
Fetch Code Content (GitHub API)
    ↓
Render Code as Screenshot (syntax highlighted)
    ↓
DeepSeek OCR Compression
    ↓
Include Compressed Context in LLM Prompt
    ↓
Generate Issue Content with Full Context
```

### Technical Implementation

**1. Code Rendering**:

```python
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from PIL import Image

def render_code_to_image(code: str, language: str):
    lexer = get_lexer_by_name(language)
    formatter = ImageFormatter(
        style="monokai",
        line_numbers=True,
        font_size=12
    )

    image_bytes = highlight(code, lexer, formatter)
    return Image.open(io.BytesIO(image_bytes))
```

**2. OCR Compression**:

```python
import deepseek

def compress_with_ocr(code_files: List[str]):
    images = [render_code_to_image(file.content, file.language) for file in code_files]

    # DeepSeek OCR compression
    compressed_tokens = deepseek.ocr_compress(
        images=images,
        compression_ratio=10,
        maintain_precision=0.97
    )

    return compressed_tokens
```

**3. LLM Integration**:

```python
def generate_issue_with_full_context(feature_request: str, code_files: List[str]):
    compressed_context = compress_with_ocr(code_files)

    prompt = f"""
    Feature Request: {feature_request}

    Codebase Context (compressed):
    {compressed_context}

    Generate a GitHub issue with:
    - Title
    - Description
    - Acceptance criteria
    - Impacted files analysis
    """

    response = llm.complete(prompt, max_tokens=2000)
    return response
```

### Benefits

- **10x context expansion**: Include entire feature codebases in prompts
- **Cost reduction**: Visual tokens are cheaper than text tokens
- **Better accuracy**: LLM has full context for decision-making
- **Screenshot support**: Can process design mockups and documentation images

### Use Cases

**1. Large Feature Analysis**:
Include all related files (10-50 files) in a single LLM call without exceeding context limits.

**2. Design-to-Code**:
Process Figma screenshots or mockups to generate implementation issues.

**3. Documentation Parsing**:
Extract requirements from PDF documentation or wiki screenshots.

### Technical Requirements

**Dependencies**:
- DeepSeek API access (or equivalent OCR compression model)
- Pygments (code syntax highlighting)
- PIL/Pillow (image processing)

**Integration Points**:
- Add HTTP Request block for DeepSeek API
- Modify PR generation module to include compressed context
- Update cost estimation (visual tokens vs text tokens)

### Implementation Priority

**Phase 1** (Research):
- Evaluate DeepSeek API availability and pricing
- Benchmark compression ratios and precision
- Test integration with existing workflow

**Phase 2** (MVP):
- Implement basic code-to-image rendering
- Integrate DeepSeek OCR compression
- Compare issue quality with/without compression

**Phase 3** (Production):
- Optimize rendering performance
- Add caching for frequently accessed code
- Implement adaptive compression (adjust ratio based on file importance)

---

## Conflict Detection and Co-Change Analysis

### Problem Statement

Engineers often work on overlapping code without awareness of each other's changes, leading to:

- **Merge conflicts**: Wasted time resolving conflicting changes
- **Duplicate work**: Multiple engineers solving the same problem
- **Integration issues**: Changes that break each other's functionality

### Proposed Solution

Implement intelligent conflict detection that analyzes:

1. **File-level conflicts**: Which files are being modified in open PRs
2. **Co-change patterns**: Files that historically change together
3. **Semantic conflicts**: Code changes that don't conflict textually but break functionality

### Architecture

```
Feature Request → Impacted Files Identified
    ↓
Check Open PRs for File Overlaps
    ↓
Analyze Git History for Co-Change Patterns
    ↓
Calculate Conflict Risk Score
    ↓
Generate Warning in Issue + Slack Notification
```

### Technical Implementation

**1. File-Level Conflict Detection**:

```python
def detect_file_conflicts(impacted_files: List[str], repo: str):
    open_prs = github.get_open_prs(repo)

    conflicts = []
    for pr in open_prs:
        pr_files = github.get_pr_files(pr.number)
        overlapping_files = set(impacted_files) & set(pr_files)

        if overlapping_files:
            conflicts.append({
                "pr_number": pr.number,
                "pr_title": pr.title,
                "overlapping_files": list(overlapping_files),
                "pr_author": pr.author
            })

    return conflicts
```

**2. Co-Change Pattern Analysis**:

```python
def analyze_cochange_patterns(file_path: str, lookback_days: int = 90):
    # Get commit history
    commits = git.log(f"--since={lookback_days} days ago", "--name-only")

    # Build co-change matrix
    cochange_count = defaultdict(int)
    for commit in commits:
        changed_files = commit.files
        if file_path in changed_files:
            for other_file in changed_files:
                if other_file != file_path:
                    cochange_count[other_file] += 1

    # Calculate co-change probability
    file_commit_count = len([c for c in commits if file_path in c.files])
    cochange_probability = {
        file: count / file_commit_count
        for file, count in cochange_count.items()
    }

    # Return files that change together > 50% of the time
    return [file for file, prob in cochange_probability.items() if prob > 0.5]
```

**3. Risk Score Calculation**:

```python
def calculate_conflict_risk(impacted_files: List[str], repo: str):
    file_conflicts = detect_file_conflicts(impacted_files, repo)

    risk_score = 0.0
    warnings = []

    # Direct file overlap (highest risk)
    if file_conflicts:
        risk_score += 0.5 * len(file_conflicts)
        warnings.append(f"Overlaps with {len(file_conflicts)} open PRs")

    # Co-change analysis (medium risk)
    for file in impacted_files:
        cochange_files = analyze_cochange_patterns(file)
        for cofile in cochange_files:
            if is_modified_in_open_pr(cofile):
                risk_score += 0.2
                warnings.append(f"{file} often changes with {cofile} (modified in PR #{pr})")

    # Normalize risk score (0-1)
    risk_score = min(risk_score, 1.0)

    return {
        "risk_score": risk_score,
        "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.3 else "low",
        "warnings": warnings
    }
```

**4. Issue Enhancement**:

```markdown
## Conflict Risk Analysis

**Risk Level**: High (0.85)

### Overlapping PRs
- PR #42: Update login component (overlaps: `login.tsx`)
- PR #38: Refactor authentication (overlaps: `auth.ts`)

### Co-Change Patterns
- `login.tsx` frequently changes with `auth.ts` (78% co-occurrence)
- `auth.ts` is currently modified in PR #38

### Recommendations
- Coordinate with @engineer1 (PR #42) and @engineer2 (PR #38)
- Consider implementing this feature after PRs #42 and #38 merge
- Review integration points in `auth.ts` before starting
```

### Benefits

- **Proactive conflict awareness**: Engineers know about potential conflicts before starting work
- **Better coordination**: Automatic notifications to engineers working on related code
- **Reduced merge conflicts**: Plan work to avoid overlapping changes
- **Historical insights**: Learn which parts of codebase are tightly coupled

### Integration Points

**Postman Flow Module**:
Add new HTTP Request block after Ripgrep search to call conflict detection service.

**Slack Notifications**:
Include conflict warnings prominently in Slack message with @ mentions for relevant engineers.

**GitHub Issue**:
Add "Conflict Risk Analysis" section with actionable recommendations.

### Technical Requirements

**Data Sources**:
- GitHub API (open PRs, PR files)
- Git history (commit logs, file changes)

**Compute Requirements**:
- Co-change analysis can be pre-computed nightly
- File-level conflicts are calculated in real-time

**Storage**:
- Co-change matrix (cached in Redis or database)
- PR metadata (cached with 5-minute TTL)

### Implementation Priority

**Phase 1** (MVP):
- Implement file-level conflict detection
- Display overlapping PRs in issue

**Phase 2** (Co-Change Analysis):
- Analyze git history for co-change patterns
- Calculate risk scores
- Add recommendations section

**Phase 3** (Advanced):
- Semantic conflict detection (analyze code dependencies)
- Calendar integration (engineer availability)
- Auto-merge suggestions for low-risk PRs

---

## Analytics Dashboard

### Problem Statement

Current workflow provides limited visibility into:

- **Reasoning traces**: How AI Agent makes decisions
- **Performance metrics**: Response times, success rates
- **Usage patterns**: Which features are most requested
- **Cost tracking**: API usage and LLM token consumption

### Proposed Solution

Build a Next.js dashboard that visualizes workflow execution, AI reasoning, and system metrics.

### Architecture

```
Postman Flow → Webhook → Dashboard API (Express)
                             ↓
                      Store in Database
                             ↓
                      Dashboard UI (Next.js)
```

### Features

**1. Workflow Visualization**:

Display each Action execution with:
- Timeline view (Request → Evaluate → Validate → Module → Response)
- Block-level timing (identify bottlenecks)
- Success/failure indicators
- Input/output data for each block

**2. Reasoning Traces**:

Show AI Agent decision-making process:
- Tool selection rationale
- Query transformations
- Confidence scores
- Alternative paths considered

**3. Metrics Dashboard**:

**Performance Metrics**:
- Average execution time (p50, p95, p99)
- Success rate (by feature type)
- Error rate (by error type)

**Usage Metrics**:
- Requests per day/week/month
- Most requested features
- Active users (by Slack user ID)

**Cost Metrics**:
- API call count (Ripgrep, GitHub, LLM)
- Token usage (LLM input/output tokens)
- Estimated cost per request

**4. Issue History**:

List all generated issues with:
- Feature request (original Slack command)
- Impacted files
- Conflict risk score
- GitHub issue link
- Created at timestamp

### Technical Implementation

**Dashboard API** (Express.js):

```typescript
// Store workflow execution
app.post("/api/webhook", async (req, res) => {
  const execution = {
    action_id: req.body.action_id,
    run_id: req.body.run_id,
    status: req.body.status,
    duration_ms: req.body.duration_ms,
    blocks: req.body.blocks,  // Timing for each block
    inputs: req.body.inputs,
    outputs: req.body.outputs,
    timestamp: new Date()
  };

  await db.collection("executions").insertOne(execution);
  res.status(200).send("OK");
});

// Get metrics
app.get("/api/metrics", async (req, res) => {
  const { start_date, end_date } = req.query;

  const executions = await db.collection("executions")
    .find({
      timestamp: { $gte: start_date, $lte: end_date }
    })
    .toArray();

  const metrics = {
    total_requests: executions.length,
    success_rate: executions.filter(e => e.status === "success").length / executions.length,
    avg_duration_ms: executions.reduce((sum, e) => sum + e.duration_ms, 0) / executions.length,
    error_breakdown: groupBy(executions.filter(e => e.status === "error"), "error.type")
  };

  res.json(metrics);
});
```

**Dashboard UI** (Next.js):

```typescript
"use client";

import { useEffect, useState } from "react";
import { Line, Bar } from "react-chartjs-2";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState(null);
  const [executions, setExecutions] = useState([]);

  useEffect(() => {
    fetch("/api/metrics?start_date=2025-01-01")
      .then(res => res.json())
      .then(data => setMetrics(data));

    fetch("/api/executions?limit=100")
      .then(res => res.json())
      .then(data => setExecutions(data));
  }, []);

  return (
    <div>
      <h1>Relay Dashboard</h1>

      <section>
        <h2>Performance Metrics</h2>
        <MetricCard title="Success Rate" value={`${(metrics?.success_rate * 100).toFixed(1)}%`} />
        <MetricCard title="Avg Duration" value={`${metrics?.avg_duration_ms}ms`} />
        <MetricCard title="Total Requests" value={metrics?.total_requests} />
      </section>

      <section>
        <h2>Execution Timeline</h2>
        <Line data={createTimelineData(executions)} />
      </section>

      <section>
        <h2>Recent Executions</h2>
        <ExecutionList executions={executions} />
      </section>
    </div>
  );
}
```

### Benefits

- **Debugging**: Quickly identify which block causes failures
- **Optimization**: Find bottlenecks and optimize slow operations
- **Transparency**: Show stakeholders how the system makes decisions
- **Cost control**: Track and optimize API usage

### Technical Requirements

**Backend**:
- Express.js API (port 3002)
- MongoDB or PostgreSQL (execution storage)
- Redis (caching)

**Frontend**:
- Next.js 14+ (App Router)
- Chart.js or Recharts (visualizations)
- Tailwind CSS (styling)

**Infrastructure**:
- DigitalOcean App Platform (backend)
- Vercel (frontend)

### Implementation Priority

**Phase 1** (MVP):
- Basic execution list
- Success/failure metrics
- Simple timeline visualization

**Phase 2** (Enhanced):
- Reasoning trace visualization
- Cost tracking
- Filtering and search

**Phase 3** (Advanced):
- Real-time updates (WebSockets)
- Anomaly detection
- Predictive analytics

---

## CI/CD Integration

### Problem Statement

Currently, issues are created manually. The next logical step is to automate PR creation and submission for review.

### Proposed Solution

Integrate with GitHub Actions to:
1. Create feature branch automatically
2. Generate code changes (using AI)
3. Submit PR for review
4. Run tests in CI pipeline

### Architecture

```
Issue Created (via Relay)
    ↓
GitHub Actions Workflow Triggered
    ↓
Generate Code Changes (Claude/GPT-4)
    ↓
Create Branch + Commit Changes
    ↓
Open Pull Request
    ↓
Run Tests (CI Pipeline)
    ↓
Notify Engineers (Slack + GitHub)
```

### Technical Implementation

**.github/workflows/auto-pr.yml**:

```yaml
name: Auto-Generate PR from Issue

on:
  issues:
    types: [labeled]

jobs:
  generate-pr:
    if: contains(github.event.issue.labels.*.name, 'auto-pr')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Extract Issue Details
        id: issue
        run: |
          echo "title=${{ github.event.issue.title }}" >> $GITHUB_OUTPUT
          echo "body=${{ github.event.issue.body }}" >> $GITHUB_OUTPUT

      - name: Generate Code Changes
        id: generate
        uses: ./actions/generate-code
        with:
          issue_title: ${{ steps.issue.outputs.title }}
          issue_body: ${{ steps.issue.outputs.body }}
          model: "claude-sonnet-4"

      - name: Create Branch and Commit
        run: |
          git checkout -b auto-pr/${{ github.event.issue.number }}
          git add .
          git commit -m "feat: ${{ steps.issue.outputs.title }}"
          git push origin auto-pr/${{ github.event.issue.number }}

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: ${{ steps.issue.outputs.title }}
          body: |
            Auto-generated from #${{ github.event.issue.number }}

            ${{ steps.generate.outputs.pr_description }}
          branch: auto-pr/${{ github.event.issue.number }}
          labels: auto-generated
```

### Benefits

- **End-to-end automation**: From Slack command to code changes
- **Faster iteration**: PRs ready for review in minutes
- **Consistent quality**: Generated code follows project conventions
- **Test coverage**: Auto-run tests before human review

### Implementation Priority

**Phase 1** (Research):
- Evaluate code generation quality (Claude vs GPT-4)
- Test on small, well-defined features

**Phase 2** (Limited Rollout):
- Enable for specific issue types (bug fixes, UI tweaks)
- Require human approval before merge

**Phase 3** (Full Automation):
- Auto-merge low-risk PRs after tests pass
- Integrate with code review tools

---

## Multi-Repository Support

### Problem Statement

Many organizations have microservices architectures where features span multiple repositories.

### Proposed Solution

Extend Relay to:
1. Search across multiple repositories
2. Detect cross-repo dependencies
3. Create coordinated issues/PRs in multiple repos

### Architecture

```
Feature Request → Identify Impacted Services
    ↓
Search Each Repository (parallel)
    ↓
Detect Cross-Repo Dependencies
    ↓
Create Issues in Each Repo (with links)
    ↓
Notify Team with Dependency Graph
```

### Technical Requirements

- Multi-repo configuration in Postman environment
- Parallel Ripgrep API calls (using Postman Flow parallelization)
- Dependency graph visualization

### Implementation Priority

**Phase 2-3** (after core features stabilize)

---

## Implementation Timeline

**Q1 2025**:
- Elasticsearch vector search (MVP)
- Conflict detection (file-level)
- Analytics dashboard (MVP)

**Q2 2025**:
- DeepSeek OCR integration (research + MVP)
- Co-change analysis
- CI/CD integration (limited rollout)

**Q3 2025**:
- Multi-repository support
- Advanced conflict detection (semantic)
- Dashboard enhancements (real-time updates)

**Q4 2025**:
- Full automation (auto-merge low-risk PRs)
- Predictive analytics
- Enterprise features (SSO, audit logs)

---

## Contributing

If you want to contribute to any of these features:

1. Review the feature design in this document
2. Create a GitHub issue proposing your implementation approach
3. Discuss technical details with maintainers
4. Submit a PR with comprehensive tests and documentation

See [CLAUDE.md](./CLAUDE.md) for development guidelines.

---

## References

- [Elasticsearch k-NN Search](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [DeepSeek OCR Research](https://github.com/deepseek-ai/DeepSeek-Coder)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Co-Change Pattern Analysis](https://arxiv.org/abs/1710.00304)
