# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

---

## Project Overview

**"You Are Absolutely Right"** is a **PM Copilot** that transforms vague product specifications into actionable GitHub PRs—all from a single Slack command.

### The Problem We Solve

**PM says**: "Add dark mode toggle to settings"

**What happens without us**:
- Engineer spends 20 min clarifying requirements
- 15 min searching codebase for relevant files
- 30 min drafting PR with acceptance criteria
- 10 min checking for conflicts with open PRs

**Total**: 75 minutes of manual work for a simple feature request.

**Our Solution**: Automate the entire workflow in 30 seconds using Postman Flows orchestration + AI-powered code generation.

---

## How It Works (End-to-End)

1. **PM types in Slack**: `/impact "Add dark mode toggle to settings"`
2. **Postman Flow** (deployed as Action) receives webhook
3. **Ripgrep API** searches codebase for relevant files (Settings.tsx, theme.ts)
4. **AI Agent** checks open PRs for conflicts
5. **Claude API** drafts PR with code changes + acceptance criteria
6. **GitHub API** creates pull request
7. **Slack** notifies team with reasoning trace
8. **Result**: GitHub PR #43 created in 30 seconds

---

## Tech Stack

### Core Technologies

**Postman Flows**
- **AI Agent Block**: GPT-5 powered autonomous orchestration
- **Flow Modules**: 6 reusable tools (Ripgrep, GitHub, Claude, Slack, etc.)
- **Actions**: Deployed flow with public URL for Slack integration
- **Analytics**: Tool call logging and reasoning visibility

**APIs Integrated**
1. **Ripgrep API**: Code search (Node.js wrapper around ripgrep CLI)
2. **Claude API**: PR generation and acceptance criteria (Sonnet 4.5)
3. **GitHub REST API**: Pull request creation
4. **Slack Webhooks**: Block Kit notifications with reasoning traces

**Dashboard** (Optional)
- **Frontend**: Next.js 16 (App Router, React 19)
- **Backend**: Express.js (analytics API on port 3002)
- **Purpose**: Visualize PR history, reasoning traces, metrics

---

## Architecture

```
Slack: /impact "fix mobile login"
    ↓
Postman AI Agent (Orchestrator)
    │
    ├─→ Ripgrep API: Search codebase
    │   Returns: ["src/pages/Login.tsx", "src/styles/mobile.css"]
    │
    ├─→ GitHub API: Check open PRs for conflicts
    │   Detects overlaps, calculates risk score
    │
    ├─→ Claude API: Generate PR content
    │   Creates: title, description, acceptance criteria
    │
    ├─→ GitHub API: Create pull request
    │   Returns: PR #43 URL
    │
    └─→ Slack Webhook: Notify team
        Shows: PR link, impacted files, conflict warnings, reasoning trace
```

---

## Project Structure

```
youareabsolutelyright/
├── postman/
│   ├── modules/              # 6 Flow Modules (AI Agent tools)
│   │   ├── ripgrep-search-module.json
│   │   ├── get-open-prs-module.json
│   │   ├── get-pr-files-module.json
│   │   ├── claude-generate-pr-module.json
│   │   ├── create-github-pr-module.json
│   │   └── send-slack-notification-module.json
│   ├── AI-AGENT-CONFIGURATION.md  # Prompt + setup guide
│   └── collections/          # Reusable API collections
│
├── ripgrep-api/              # Code search API (Node.js/Express)
│   ├── src/
│   │   ├── index.js         # Server
│   │   ├── routes/search.js # Search endpoint
│   │   └── services/ripgrep.js
│   ├── package.json
│   └── .env                 # PORT=3001
│
├── dashboard-api/            # Analytics backend (Express.js)
│   ├── src/
│   │   ├── index.js
│   │   └── routes/webhook.js
│   └── package.json
│
├── frontend/                 # Dashboard (Next.js)
│   ├── app/
│   │   ├── page.tsx         # Home (redirects to dashboard)
│   │   └── dashboard/page.tsx
│   └── package.json
│
├── backend/                  # Optional: For MLH hackathon integration
│   └── (See SNOWFLAKE_MLH.md for details)
│
├── docs/                     # Documentation
│   ├── POSTMAN_FLOW_NEW_FEATURES.md
│   ├── POSTMAN_FLOW_FIX_GUIDE.md
│   ├── DEV2_POSTMAN_GUIDE.md
│   └── CI_CD_SETUP.md
│
├── CLAUDE.md                 # This file
├── README.md                 # Public-facing project overview
├── SETUP.md                  # Single setup guide
└── SNOWFLAKE_MLH.md          # MLH hackathon Snowflake integration
```

---

## Development Setup

### 1. Ripgrep API (Code Search)

```bash
cd ripgrep-api
npm install
cp .env.example .env
# Edit .env: PORT=3001
npm run dev
```

**Health check**: `curl http://localhost:3001/api/health`

**Test search**:
```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"ProfileCard","path":"src/","type":"tsx"}'
```

**Key Features**:
- Returns `is_new_feature: true` when no files found
- Provides helpful context for Claude API
- Supports glob patterns, case sensitivity, file type filters

### 2. Postman Flows

**Setup Flow Modules**:
1. Open Postman Desktop (v11.42.3+)
2. Import all modules from `postman/modules/`
3. For each collection → Right-click → "Create Flow Module"

**Configure AI Agent**:
1. Create new Flow: "PM-Copilot-Main"
2. Add blocks: Start → AI Agent → Output
3. In AI Agent:
   - Add all 6 flow modules as tools
   - Copy system prompt from `postman/AI-AGENT-CONFIGURATION.md`
4. Deploy as Action (get public URL)

**Environment Variables** (in Postman):
```
RIPGREP_API_URL = http://localhost:3001
CLAUDE_API_KEY = sk-ant-...
GITHUB_TOKEN = ghp_... (with repo scope)
SLACK_WEBHOOK_PM = https://hooks.slack.com/services/...
REPO_OWNER = V-prajit
REPO_NAME = youareabsolutelyright
```

### 3. Slack Integration

**Create Slack App**:
1. Go to https://api.slack.com/apps → Create New App
2. Enable **Slash Commands**:
   - Command: `/impact`
   - Request URL: {Your Postman Action URL}
   - Description: "Generate PR from feature request"
3. Enable **Incoming Webhooks**:
   - Add webhook to #new-channel
   - Copy webhook URL to Postman environment
4. Install app to workspace

**Test**:
```
/impact "Add dark mode toggle to settings"
```

### 4. Dashboard (Optional)

```bash
# Terminal 1: Backend API
cd dashboard-api
npm install && npm run dev  # Port 3002

# Terminal 2: Frontend
cd frontend
npm install && npm run dev  # Port 3000
```

Visit: http://localhost:3000/dashboard

---

## Key Files & Configuration

### Ripgrep API Environment

**File**: `ripgrep-api/.env`
```env
PORT=3001
ALLOWED_ORIGINS=*
MAX_SEARCH_RESULTS=50
DEFAULT_SEARCH_PATH=./
```

### Postman Flow Modules

**Ripgrep Search Module**:
- **Input**: `query`, `path`, `type`, `case_sensitive`
- **Output**: `files[]`, `total`, `is_new_feature`, `message`

**Claude Generate PR Module**:
- **Input**: `feature_request`, `impacted_files[]`, `is_new_feature`, `repo_name`
- **Output**: `pr_title`, `pr_description`, `branch_name`

**Create GitHub PR Module**:
- **Input**: `pr_title`, `pr_description`, `branch_name`
- **Output**: `pr_url`, `pr_number`

**Send Slack Notification Module**:
- **Input**: `feature_name`, `pr_number`, `pr_url`, `impacted_files[]`, `conflict_score`, `reasoning_trace[]`
- **Output**: Slack Block Kit message

### AI Agent Prompt Structure

See `postman/AI-AGENT-CONFIGURATION.md` for full prompt. Key sections:

1. **Parse Intent**: Extract feature name, search keywords, acceptance criteria
2. **Search Codebase**: Call Ripgrep Search Module
3. **Conflict Detection**: Check open PRs, calculate overlap scores
4. **Generate PR**: Call Claude API with context
5. **Create PR**: Call GitHub API
6. **Notify Team**: Send Slack message with reasoning trace

---

## Handling New Features

**Problem**: When PM requests completely new features (e.g., "add OAuth"), Ripgrep returns no files.

**Solution**: Ripgrep API returns structured response with `is_new_feature` flag.

**Flow**:
1. **Ripgrep Response** (no files found):
   ```json
   {
     "files": [],
     "total": 0,
     "is_new_feature": true,
     "message": "No existing files found - may be a new feature..."
   }
   ```

2. **Claude API adapts**:
   - Reads `is_new_feature: true`
   - Creates new file structure instead of modifying existing files
   - Suggests integration points

**Examples**:
- New feature: `/impact "add oauth"` → Creates new auth files
- Existing feature: `/impact "update ProfileCard"` → Modifies existing component

**See**: `docs/POSTMAN_FLOW_NEW_FEATURES.md` for detailed guide

---

## Troubleshooting

### Ripgrep API Issues

**Port Conflict** (was both on 8000):
- **Solution**: Changed Ripgrep to port 3001 in `.env`
- Verify: `lsof -i :3001`

**404 on Search**:
- Check URL: `http://localhost:3001/api/search` (not `/search`)
- Verify server is running: `npm run dev`

### Postman Flow Issues

**422 Error on API Calls**:
- **Cause**: Missing `Content-Type: application/json` header
- **Solution**: Add header to all HTTP blocks
- See: `docs/POSTMAN_FLOW_FIX_GUIDE.md`

**Variable Not Found**:
- **Cause**: Block name doesn't match variable path
- **Solution**: Use exact block name, case-sensitive
- Example: `{{RIPGREP API.body.data.files}}` requires block named "RIPGREP API"

**Evaluate Block Errors**:
- **"data is not defined"**: Use `{{variable}}` syntax, not `data.variable`
- **"return not in function"**: Use `({ key: value })` not `return { key: value }`

### GitHub API Issues

**PR Not Created**:
- Check token: `ghp_...` with `repo` scope
- Verify `REPO_OWNER` and `REPO_NAME` are correct
- Test: `curl https://api.github.com/repos/{owner}/{repo}/pulls -H "Authorization: Bearer {token}"`

### Slack Issues

**Command Not Showing**:
- Reinstall Slack app
- Verify command appears when typing `/` in Slack

**No Notification**:
- Test webhook: `curl -X POST {webhook_url} -d '{"text":"test"}'`
- Check webhook is for correct channel
- Verify `SLACK_WEBHOOK_PM` variable is set

### Quick Health Checks

```bash
# Ripgrep API
curl http://localhost:3001/api/health

# Dashboard API
curl http://localhost:3002/api/health

# Check running services
lsof -i :3001,3002

# Restart services
cd ripgrep-api && npm run dev
cd dashboard-api && npm run dev
cd frontend && npm run dev
```

---

## Demo Flow (For Postman Hiring)

**What to Show**:

1. **Problem Statement** (15 sec):
   > "PMs waste 75 minutes per feature request on clarifications, code searches, and PR drafting. We automate this in 30 seconds."

2. **Live Demo** (30 sec):
   - Show Slack: `/impact "Add dark mode toggle"`
   - Show notification: PR created, files impacted, reasoning trace
   - Open GitHub PR: Click View PR button

3. **Technical Deep Dive** (45 sec):
   - Postman Flows analytics: Show AI Agent tool calls
   - Ripgrep API: Code search results
   - Claude API: PR generation
   - Architecture diagram

4. **Value Proposition** (30 sec):
   - Speed: 30 seconds vs 75 minutes
   - Accuracy: Code search finds exact files
   - Clarity: Auto-generated acceptance criteria
   - Traceability: Reasoning trace shows every decision

**Judge-Clickable Proof**:
- Live Postman Action URL
- Live Slack integration
- GitHub repo with generated PRs
- Dashboard with analytics

---

## Postman-Specific Features

### Why Postman Flows?

**Multi-API Orchestration**: Single flow coordinates 4 APIs (Ripgrep, Claude, GitHub, Slack)

**AI Agent Autonomy**: No manual loops or decision blocks—AI decides workflow dynamically

**Flow Modules**: Reusable tools promote clean architecture

**Actions**: Public URL deployment makes Slack integration trivial

**Analytics**: Full visibility into AI decisions for debugging and demos

### Judging Criteria Alignment

**Use of Postman Technology (20%)**:
- ✅ AI Agent Block (autonomous reasoning)
- ✅ Flow Modules (6 reusable tools)
- ✅ Actions (deployed with public URL)
- ✅ Analytics (tool call logs, reasoning traces)

**Functionality (25%)**:
- ✅ Multi-step reasoning (parse → search → detect conflicts → generate → create)
- ✅ Real-time decision making
- ✅ Error handling and retry logic
- ✅ End-to-end workflow (Slack → GitHub)

**Innovation (20%)**:
- ✅ "Receipts-first" design (every decision has code citations)
- ✅ Tiny PR constraint (≤30 lines keeps PRs reviewable)
- ✅ AI-driven conflict detection
- ✅ Reasoning transparency

**Real-World Impact (20%)**:
- ✅ Solves PM→Engineer handoff friction
- ✅ 30-second PR creation (vs 75 minutes manual)
- ✅ Team visibility via Slack
- ✅ Production-ready architecture

**UX (15%)**:
- ✅ Clean Slack UI (Block Kit formatting)
- ✅ Dashboard visualizer (optional)
- ✅ Clear demo flow
- ✅ Judge-clickable proof

---

## Future Enhancements

**Phase 2: Advanced Conflict Detection**
- Calendar + Slack Bot: Check engineer availability
- Co-change analysis: Files that change together
- Historical conflict patterns

**Phase 3: Project Management**
- Asana/Jira integration: Auto-create tasks
- Link back to GitHub PR
- Assign based on code ownership

**Phase 4: Enhanced AI**
- CodeRabbit: Automated AI code review on PRs
- Multi-model routing: GPT-5 for orchestration, Claude for code
- Advanced context analysis for complex PRs

---

## MLH Hackathon Integration

> **Note**: For Cal Hacks 12.0 MLH hackathon, we built a Snowflake Cortex integration for cost savings and data warehousing. See `SNOWFLAKE_MLH.md` for details.

**For Postman hiring focus**: This integration is optional and not core to the PM Copilot narrative.

---

## Contributing Guidelines

**When Adding Features**:
1. Create new Flow Module if adding API integration
2. Update AI Agent prompt to reference new tool
3. Add error handling for new failure modes
4. Document in this file and README
5. Test end-to-end via Slack

**Code Style**:
- **Ripgrep API**: JavaScript ES6+, Express patterns
- **Frontend**: React 19 functional components, App Router
- **Postman**: JSON collections, descriptive names

**Git Workflow**:
- Main branch: `main`
- Feature branches: `feature/feature-name`
- `.env` files are gitignored
- Commit messages: [Conventional Commits](https://www.conventionalcommits.org/)

---

## Resources

**Postman Documentation**:
- [AI Agent Block](https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/)
- [Deploy Flows as Actions](https://learning.postman.com/docs/postman-flows/build-flows/actions/)
- [Flow Modules](https://learning.postman.com/docs/postman-flows/reference/modules/)

**API Documentation**:
- [Claude Messages API](https://docs.claude.com/en/api/messages)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Slack Block Kit](https://docs.slack.dev/block-kit/)

**Project Documentation**:
- `README.md` - Public-facing overview
- `SETUP.md` - Complete setup guide
- `postman/AI-AGENT-CONFIGURATION.md` - AI Agent prompt + config
- `docs/POSTMAN_FLOW_NEW_FEATURES.md` - Handling new features
- `docs/POSTMAN_FLOW_FIX_GUIDE.md` - Common fixes
- `SNOWFLAKE_MLH.md` - MLH hackathon Snowflake integration

---

## Quick Reference Commands

```bash
# Start Ripgrep API
cd ripgrep-api && npm run dev

# Start Dashboard API
cd dashboard-api && npm run dev

# Start Frontend
cd frontend && npm run dev

# Test Ripgrep
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"import"}'

# Check ports
lsof -i :3001,3002,3000

# Kill all services
lsof -ti:3001,3002,3000 | xargs kill -9
```

---

## License

MIT License - See LICENSE file

---

**Built for Postman + Cal Hacks 12.0 - January 2025**

**Problem**: PM→Engineer handoff friction
**Solution**: Postman Flows orchestration + AI-powered automation
**Result**: 30 seconds from Slack to GitHub PR
