# You Are Absolutely Right

**PM Copilot** - Transform vague PM specs into actionable GitHub PRs in 30 seconds, all from a single Slack command.

---

## The Problem

**PM says**: "Add dark mode toggle to settings"

**What happens next** (traditional workflow):
- 20 min: Engineer asks clarifying questions
- 15 min: Searching codebase for relevant files
- 30 min: Drafting PR with acceptance criteria
- 10 min: Checking for conflicts with open PRs

**Total**: 75 minutes of manual work for a simple feature request.

---

## Our Solution

Automate the entire PM→Engineer handoff using **Postman Flows orchestration** + **AI-powered code generation**.

```
Slack: /impact "Add dark mode toggle"
    ↓ (30 seconds)
GitHub: PR #43 created ✓
```

---

## How It Works

1. **PM types in Slack**: `/impact "Add dark mode toggle to settings"`
2. **Postman AI Agent** orchestrates the workflow autonomously
3. **Ripgrep API** searches codebase for relevant files
4. **AI checks open PRs** for potential conflicts
5. **Claude API** generates PR with code + acceptance criteria
6. **GitHub API** creates pull request
7. **Slack** notifies team with reasoning trace

**Result**: Complete GitHub PR in 30 seconds with full context.

---

## Demo

### Live Example

**Input** (in Slack):
```
/impact "Fix mobile login responsive design"
```

**Output** (30 seconds later):
```
✅ PR Created: fix-mobile-login-responsive

Feature Request: Fix mobile login responsive design
Files Impacted: 2
  - src/pages/Login.tsx
  - src/styles/mobile.css

Conflict Check: ✓ No conflicts with open PRs

Reasoning Trace:
  1. Parsed intent: mobile-login-fix
  2. Searched codebase: found 2 files
  3. Scanned 3 open PRs
  4. No conflicts detected
  5. Generated PR content with Claude
  6. Created GitHub PR #45
  7. Sent notification to Slack

[View PR] [View Files]
```

**GitHub PR**: Automatically created with title, description, acceptance criteria, and branch.

---

## Key Features

### 1. Postman AI Agent Orchestration
- **Autonomous workflow**: No manual loops or decision blocks
- **Multi-API coordination**: Ripgrep, Claude, GitHub, Slack
- **Reasoning transparency**: Shows every decision step
- **Flow Modules**: 6 reusable tools for clean architecture

### 2. Intelligent Code Search
- **Ripgrep API**: Fast code search with glob patterns
- **New feature detection**: Handles both new features and existing code
- **Context-aware**: Returns `is_new_feature` flag for smarter PR generation

### 3. Smart Conflict Detection
- **Checks open PRs**: Scans for file overlaps
- **Risk scoring**: Calculates conflict percentage
- **Proactive warnings**: Alerts team before conflicts happen
- **Collaboration suggestions**: Links to conflicting PRs

### 4. Clean Slack Integration
- **Slash command**: `/impact "feature request"`
- **Rich notifications**: Block Kit formatting with buttons
- **Reasoning traces**: Shows AI's decision process
- **One-click PR viewing**: Direct links to GitHub

---

## Tech Stack

### Core Technologies

**Postman Flows**
- AI Agent Block (GPT-5 autonomous reasoning)
- Flow Modules (6 reusable tools)
- Actions (deployed with public URL)
- Analytics (tool call logging)

**APIs**
- Ripgrep API (Node.js/Express code search)
- Claude API (Sonnet 4.5 for PR generation)
- GitHub REST API (PR creation)
- Slack Webhooks (Block Kit notifications)

**Dashboard** (Optional)
- Next.js 16 + React 19 (App Router)
- Express.js backend (analytics)
- TailwindCSS (styling)

---

## Quick Start

### Prerequisites

- Postman Desktop (v11.42.3+)
- Node.js 18+
- GitHub Personal Access Token (`repo` scope)
- Slack App with Incoming Webhook
- Claude API Key

### 1. Setup Ripgrep API

```bash
cd ripgrep-api
npm install
cp .env.example .env
# Edit .env: Set PORT=3001
npm run dev
```

Verify: `curl http://localhost:3001/api/health`

### 2. Import Postman Flow Modules

1. Open Postman Desktop
2. Import all modules from `postman/modules/`
3. For each collection → Right-click → "Create Flow Module"

### 3. Configure AI Agent

1. Create new Flow: "PM-Copilot-Main"
2. Add blocks: Start → AI Agent → Output
3. In AI Agent:
   - Add all 6 flow modules as tools
   - Copy system prompt from `postman/AI-AGENT-CONFIGURATION.md`
4. Configure environment variables:
   ```
   RIPGREP_API_URL = http://localhost:3001
   CLAUDE_API_KEY = sk-ant-...
   GITHUB_TOKEN = ghp_...
   SLACK_WEBHOOK_PM = https://hooks.slack.com/services/...
   REPO_OWNER = your-username
   REPO_NAME = your-repo
   ```

### 4. Deploy as Postman Action

1. Click "Deploy" in your flow
2. Enable "Public URL"
3. Copy the Action URL

### 5. Setup Slack

1. Create Slack App at https://api.slack.com/apps
2. Enable **Slash Commands**:
   - Command: `/impact`
   - Request URL: Your Postman Action URL
3. Enable **Incoming Webhooks**:
   - Add webhook to your channel
   - Copy webhook URL to Postman environment
4. Install app to workspace

### 6. Test

In Slack:
```
/impact "Add dark mode toggle to settings"
```

Watch the magic happen! ✨

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  PM in Slack: /impact "Add ProfileCard to /users"      │
└────────────────────┬────────────────────────────────────┘
                     │ POST webhook
                     ▼
         ┌───────────────────────────┐
         │  Postman Action (Cloud)   │
         │  • Public URL endpoint    │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  AI Agent Block (GPT-5)   │
         │  • Parse PM intent        │
         │  • Orchestrate workflow   │
         │  • Make decisions         │
         └───────────┬───────────────┘
                     │
         ┌───────────┴──────────────────┬────────────┐
         │                              │            │
         ▼                              ▼            ▼
    ┌─────────────┐            ┌───────────┐  ┌──────────┐
    │ Ripgrep API │            │ GitHub    │  │ Claude   │
    │ Find files  │            │ API       │  │ API      │
    └──────┬──────┘            └─────┬─────┘  └────┬─────┘
           │                         │             │
           └─────────────┬───────────┴─────────────┘
                         ▼
              ┌──────────────────┐
              │ Slack Webhook    │
              │ Notify team      │
              └──────────────────┘
```

---

## Why Postman Flows?

### Multi-API Orchestration
Single flow coordinates 4 different APIs seamlessly

### AI Agent Autonomy
No manual loops or decision blocks—AI decides workflow steps dynamically

### Flow Modules
Reusable tools promote clean, maintainable architecture

### Public URL Deployment
Actions make Slack integration trivial (one URL, done)

### Built-in Analytics
Full visibility into AI decisions for debugging and demos

---

## Project Structure

```
youareabsolutelyright/
├── postman/
│   ├── modules/              # 6 Flow Modules
│   ├── AI-AGENT-CONFIGURATION.md
│   └── collections/
├── ripgrep-api/              # Code search (Node.js)
├── dashboard-api/            # Analytics backend
├── frontend/                 # Dashboard (Next.js)
├── docs/                     # Guides and troubleshooting
├── README.md                 # This file
├── CLAUDE.md                 # Developer instructions
└── SETUP.md                  # Complete setup guide
```

---

## Use Cases

### For PMs
- **Faster iteration**: Feature request → PR in 30 seconds
- **Better clarity**: Auto-generated acceptance criteria
- **Full visibility**: Reasoning trace shows every step

### For Engineers
- **Less clarification**: All context provided upfront
- **Conflict awareness**: Know about PR overlaps before coding
- **Ready to code**: Files identified, PR drafted, just implement

### For Teams
- **Reduced friction**: Eliminate back-and-forth clarifications
- **Async friendly**: PM requests don't block engineers
- **Audit trail**: Slack history + reasoning traces

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **End-to-End Time** | < 30 seconds |
| **Manual Time Saved** | 75 minutes → 30 seconds |
| **APIs Orchestrated** | 4 (Ripgrep, Claude, GitHub, Slack) |
| **Conflict Detection** | Real-time (checks all open PRs) |
| **PR Size Constraint** | ≤30 lines (keeps PRs reviewable) |

---

## Demo for Hiring Managers

### What This Demonstrates

**1. Problem-Solving**
- Identified real developer pain (PM→Engineer handoff)
- Built practical, production-ready solution
- Measurable impact (75 min → 30 sec)

**2. Technical Execution**
- Postman Flows orchestration
- AI Agent autonomous reasoning
- Multi-API integration
- Clean architecture (Flow Modules)

**3. Product Thinking**
- User-focused (PM and Engineer personas)
- Reasoning transparency (trust through visibility)
- Async-friendly (Slack integration)
- Scalable design (reusable modules)

**Judge-Clickable Proof**:
- ✅ Live Postman Action URL
- ✅ Live Slack integration
- ✅ GitHub repo with generated PRs
- ✅ Postman Flows analytics (reasoning traces)

---

## Troubleshooting

### Common Issues

**Ripgrep API not responding**:
```bash
cd ripgrep-api && npm run dev
curl http://localhost:3001/api/health
```

**Postman Flow errors**:
- Check environment variables are set
- Verify GitHub token has `repo` scope
- Ensure Slack webhook URL is correct
- See `docs/POSTMAN_FLOW_FIX_GUIDE.md`

**Slack command not working**:
- Reinstall Slack app
- Verify Request URL matches Postman Action URL
- Check webhook is for correct channel

**PR not created**:
- Test GitHub token: `curl https://api.github.com/user -H "Authorization: Bearer {token}"`
- Verify REPO_OWNER and REPO_NAME are correct

See `CLAUDE.md` for comprehensive troubleshooting guide.

---

## Future Enhancements

**Phase 2: Advanced Conflict Detection**
- Co-change analysis (files that change together)
- Historical conflict patterns
- Calendar + Slack Bot for engineer availability

**Phase 3: Project Management**
- Asana/Jira integration (auto-create tasks)
- Assign PRs based on code ownership
- Link PRs to project milestones

**Phase 4: Enhanced AI**
- Multi-model routing (GPT-5 + Claude)
- CodeRabbit integration (automated code review)
- Visual context compression for large diffs

---

## Contributing

See `CLAUDE.md` for development guidelines.

**Quick Guide**:
1. Create new Flow Module for new API integrations
2. Update AI Agent prompt to reference new tools
3. Add error handling and documentation
4. Test end-to-end via Slack

---

## Resources

**Documentation**:
- `SETUP.md` - Complete setup guide
- `CLAUDE.md` - Developer instructions
- `postman/AI-AGENT-CONFIGURATION.md` - AI Agent configuration
- `docs/` - Troubleshooting guides

**Postman**:
- [AI Agent Block](https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/)
- [Flow Modules](https://learning.postman.com/docs/postman-flows/reference/modules/)
- [Deploy Actions](https://learning.postman.com/docs/postman-flows/build-flows/actions/)

**APIs**:
- [Claude API](https://docs.claude.com/en/api/messages)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Slack Block Kit](https://docs.slack.dev/block-kit/)

---

## Hackathon Context

This project was built for **Cal Hacks 12.0** (January 2025) and showcases:
- Postman Flows AI Agent capabilities
- Multi-API orchestration
- Real-world developer tooling
- Production-ready architecture

**MLH Integration**: For the hackathon, we also built a Snowflake Cortex integration for cost-optimized PR generation and data warehousing. See `SNOWFLAKE_MLH.md` for details.

---

## License

MIT License - See LICENSE file for details

---

## Contact

**Team**: youareabsolutelyright

**Demo**: https://youtu.be/your-video-here

**Postman Action**: [Live URL for judges to test]

**GitHub**: https://github.com/V-prajit/youareabsolutelyright

---

**Built with ❤️ for Postman + Cal Hacks 12.0**

*From vague PM spec to production-ready PR in 30 seconds.*
