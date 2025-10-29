# Project Index: You Are Absolutely Right

**PM Copilot** - Transform vague product specifications into actionable GitHub PRs in 30 seconds

Last Updated: 2025-10-28
Repository: youareabsolutelyright
Tech Stack: Postman Flows, Ripgrep API, Claude API, GitHub API, Slack, Next.js, Express.js

---

## Table of Contents

1. [Root Configuration Files](#root-configuration-files)
2. [Core Documentation](#core-documentation)
3. [Postman Integration](#postman-integration)
4. [Ripgrep API](#ripgrep-api)
5. [Dashboard API](#dashboard-api)
6. [Frontend (Next.js Dashboard)](#frontend-nextjs-dashboard)
7. [Backend (Python/Snowflake)](#backend-pythonsnowflake)
8. [Slack Listener Service](#slack-listener-service)
9. [Snowflake Integration](#snowflake-integration)
10. [Demo Resources](#demo-resources)
11. [Mock Repository](#mock-repository)
12. [Scripts & Utilities](#scripts--utilities)
13. [Logs & Runtime](#logs--runtime)
14. [GitHub Actions](#github-actions)

---

## Root Configuration Files

### Environment & Git
- **`.env`** - Main environment variables (gitignored, contains secrets)
- **`.env.example`** - Template for environment variables
- **`.gitignore`** - Git exclusions (node_modules, .env, logs, etc.)
- **`.gitattributes`** - Git line ending and diff settings
- **`.claude/settings.local.json`** - Claude Code local settings

### Documentation
- **`README.md`** - Public-facing project overview for hackathon/hiring
- **`CLAUDE.md`** - Comprehensive developer guide for Claude Code (THIS IS THE MAIN GUIDE)
- **`SETUP.md`** - Single setup guide for all services
- **`DEPLOYMENT_GUIDE.md`** - Production deployment instructions
- **`SNOWFLAKE_MLH.md`** - MLH hackathon Snowflake Cortex integration guide
- **`VERIFY_SNOWFLAKE.sql`** - SQL script to verify Snowflake setup
- **`PM_COPILOT_TEAM_TASKS.txt`** - Task tracking for team collaboration

---

## Core Documentation

### `/docs/` Directory

#### Postman Flow Guides
- **`POSTMAN_FLOW_FIX_GUIDE.md`** - Common fixes for Postman Flow errors (422, variable issues)
- **`DEV2_POSTMAN_GUIDE.md`** - Developer guide for Postman Flow integration
- **`FLOW_MODULES.md`** - Documentation of all 6 Flow Modules
- **`DEV2_TESTING_CHECKLIST.md`** - Testing checklist for Postman integration

#### Setup Guides
- **`MCP_SETUP.md`** - Model Context Protocol server setup
- **`CI_CD_SETUP.md`** - Continuous Integration/Deployment configuration
- **`WORKSPACE_URL.txt`** - Postman workspace URL reference

#### Downloaded Postman Documentation
- **`learning.postman.com/docs/`** - Cached Postman documentation (extensive, 200+ files)
  - Administration guides (teams, roles, SCIM, audit logs)
  - API governance and collaboration
  - Collections and flows
  - Billing and resource usage
  - Developer resources (API, SDK, runtime)

---

## Postman Integration

### `/postman/` Directory

#### AI Agent Configuration
- **`AI-AGENT-CONFIGURATION.md`** - System prompt + AI Agent setup instructions
  - Multi-step reasoning workflow
  - Tool calling conventions
  - Error handling strategies

#### Flow Modules (`/postman/modules/`)
Core reusable tools for AI Agent:

1. **`ripgrep-search-module.json`** - Code search via Ripgrep API
   - Input: query, path, type, case_sensitive
   - Output: files[], total, is_new_feature, message

2. **`get-open-prs-module.json`** - Fetch open GitHub PRs
   - Detects conflicts with existing work
   - Returns PR list with metadata

3. **`get-pr-files-module.json`** - Get files changed in a PR
   - Used for conflict detection
   - Returns file paths and change counts

4. **`claude-generate-pr-module.json`** - AI-powered PR generation
   - Input: feature_request, impacted_files[], is_new_feature
   - Output: pr_title, pr_description, branch_name, acceptance_criteria

5. **`create-github-pr-module.json`** - Create GitHub pull request
   - Creates branch and PR
   - Returns pr_url, pr_number

6. **`send-slack-notification-module.json`** - Slack Block Kit notifications
   - Sends PR link, impacted files, reasoning trace
   - Includes conflict warnings and metrics

- **`README.md`** - Flow Modules documentation and usage guide

#### Collections (`/postman/collections/`)
Reusable API request collections:

- **`ripgrep-api.json`** - Ripgrep API endpoints (search, health)
- **`claude-api.json`** - Anthropic Claude API integration
- **`github-api.json`** - GitHub REST API (PRs, branches, files)
- **`slack-webhooks.json`** - Slack webhook configurations
- **`pm-copilot-health-check.json`** - Service health monitoring
- **`snowflake-generate-pr.json`** - Snowflake Cortex integration

#### Environments (`/postman/environments/`)
Environment variable sets:

- **`pm-copilot-env.json`** - Main production environment
- **`dev.json`** - Development environment (localhost)
- **`dev-simple.json`** - Minimal dev environment
- **`production.json`** - Production environment
- **`environment.json`** - Active environment (gitignored)
- **`environment.example.json`** - Template for environment setup

**Required Variables:**
- `RIPGREP_API_URL` (http://localhost:3001)
- `CLAUDE_API_KEY` (sk-ant-...)
- `GITHUB_TOKEN` (ghp_... with repo scope)
- `SLACK_WEBHOOK_PM` (https://hooks.slack.com/...)
- `REPO_OWNER`, `REPO_NAME`

#### Flows (`/postman/flows/`)
- **`relay-command-flow.json`** - Main orchestration flow
  - Slack → Ripgrep → Claude → GitHub → Slack
  - AI Agent autonomous decision-making

#### Mock Servers (`/postman/mock-servers/`)
- **`code-samples.json`** - Mock API responses for testing

#### MCP Configuration
- **`mcp-server-config.json`** - Model Context Protocol server configuration

---

## Ripgrep API

**Port:** 3001
**Purpose:** Code search service (Node.js wrapper around ripgrep CLI)
**Location:** `/ripgrep-api/`

### Key Files

#### Source Code (`/ripgrep-api/src/`)
- **`index.js`** - Express server main entry point
  - CORS configuration
  - Route mounting
  - Health endpoint
  - Port: 3001

- **`routes/search.js`** - Search endpoint handler
  - POST `/api/search`
  - Query validation
  - Response formatting
  - New feature detection

- **`services/ripgrep.js`** - Ripgrep CLI wrapper
  - Executes ripgrep binary
  - Parses results
  - Handles errors
  - Detects new features (is_new_feature flag)

#### Configuration
- **`package.json`** - Node.js dependencies
  - express (server)
  - @vscode/ripgrep (CLI binary)
  - cors, dotenv

- **`.env`** - Service configuration (gitignored)
- **`.env.example`** - Environment template
  ```
  PORT=3001
  ALLOWED_ORIGINS=*
  MAX_SEARCH_RESULTS=50
  DEFAULT_SEARCH_PATH=./
  ```

- **`.gitignore`** - Excludes node_modules, .env, logs

#### Testing
- **`test-rg.js`** - Manual test script for ripgrep functionality

#### Documentation
- **`README.md`** - API documentation
  - Endpoints
  - Request/response formats
  - Setup instructions
  - Example curl commands

### API Endpoints
- `GET /api/health` - Health check
- `POST /api/search` - Code search
  - Body: `{ query, path, type, case_sensitive }`
  - Response: `{ files[], total, is_new_feature, message }`

---

## Dashboard API

**Port:** 3002
**Purpose:** Analytics backend for dashboard
**Location:** `/dashboard-api/`

### Key Files

#### Source Code (`/dashboard-api/src/`)
- **`index.js`** - Express server for analytics
  - Port 3002
  - CORS for frontend
  - Route mounting

- **`routes/webhooks.js`** - Webhook receiver
  - Receives PR generation events
  - Stores analytics data

- **`routes/analytics.js`** - Analytics endpoints
  - GET `/api/analytics` - Fetch metrics
  - PR history
  - Reasoning traces

- **`routes/conflicts.js`** - Conflict detection data
  - Conflict scores
  - Overlap analysis

#### Configuration
- **`package.json`** - Dependencies (express, cors)
- **`.env.example`** - Environment template

#### Documentation
- **`README.md`** - API documentation and setup

### API Endpoints
- `GET /api/health` - Health check
- `POST /api/webhook` - Receive PR events
- `GET /api/analytics` - Fetch analytics data
- `GET /api/conflicts` - Conflict analysis

---

## Frontend (Next.js Dashboard)

**Port:** 3000
**Purpose:** Visualize PR history, reasoning traces, metrics
**Location:** `/frontend/`
**Framework:** Next.js 16 (App Router), React 19

### App Router (`/frontend/app/`)

#### Pages
- **`page.tsx`** - Home page (redirects to /dashboard)
- **`layout.tsx`** - Root layout with global styles
- **`globals.css`** - Global CSS (Tailwind)
- **`favicon.ico`** - Site favicon

#### Dashboard Routes
- **`dashboard/page.tsx`** - Main dashboard view
  - PR timeline
  - Conflict graph
  - Risk meter
  - Recent PRs list

- **`dashboard/[id]/page.tsx`** - Individual PR detail view
  - Full reasoning trace
  - File impact analysis
  - Conflict warnings

### Components (`/frontend/components/`)
Reusable React components:

- **`PRTimeline.tsx`** - Timeline visualization of PR creation flow
  - Shows: Slack → Ripgrep → Claude → GitHub
  - Timestamps and status indicators

- **`ConflictGraph.tsx`** - Visual conflict detection graph
  - Shows file overlaps between PRs
  - Risk scores and warnings

- **`RiskMeter.tsx`** - Conflict risk score meter
  - 0-100 scale
  - Color-coded (green/yellow/red)

- **`ReasoningTrace.tsx`** - AI Agent reasoning steps
  - Tool calls
  - Decision points
  - Code citations

### Library (`/frontend/lib/`)
- **`api.ts`** - API client for dashboard-api
  - Fetch functions
  - Type definitions
  - Error handling

### Public Assets (`/frontend/public/`)
- **`next.svg`** - Next.js logo
- **`vercel.svg`** - Vercel logo
- **`file.svg`**, **`globe.svg`**, **`window.svg`** - UI icons

### Configuration
- **`package.json`** - Dependencies
  - next, react, react-dom
  - tailwindcss
  - TypeScript

- **`tsconfig.json`** - TypeScript configuration
  - App Router paths
  - Strict mode

- **`next.config.ts`** - Next.js configuration
  - Webpack settings
  - Environment variables

- **`eslint.config.mjs`** - ESLint rules
- **`postcss.config.mjs`** - PostCSS for Tailwind
- **`.gitignore`** - Excludes .next/, node_modules/

#### Documentation
- **`README.md`** - Frontend setup and development guide

---

## Backend (Python/Snowflake)

**Port:** 8000 (FastAPI)
**Purpose:** MLH hackathon Snowflake Cortex integration
**Location:** `/backend/`
**Framework:** FastAPI (Python)

### Main Application

#### Entry Points
- **`run.py`** - Development server runner
- **`app/main.py`** - FastAPI application setup
  - CORS middleware
  - Route mounting
  - Lifespan events

#### Routes (`/backend/app/routes/`)
- **`snowflake.py`** - Snowflake Cortex endpoints
  - PR generation via Cortex LLM
  - SQL query execution
  - Data warehousing

- **`cortex_showcase.py`** - Cortex feature demos
  - Semantic model queries
  - Analytics examples

- **`ripgrep_proxy.py`** - Proxy to Ripgrep API
  - Forwards requests to Node.js service
  - Python integration layer

- **`dashboard.py`** - Dashboard data endpoints
  - Metrics aggregation
  - Historical data

- **`deepseek.py`** - DeepSeek OCR integration
  - Visual context compression
  - Large diff handling

#### Services (`/backend/app/services/`)
- **`snowflake_service.py`** - Snowflake connection and queries
  - Connection pooling
  - Query execution
  - Error handling

- **`deepseek_service.py`** - DeepSeek API client
  - OCR processing
  - Image analysis

- **`compressor.py`** - Context compression utilities
- **`encoder.py`**, **`decoder.py`** - Data encoding/decoding
- **`image_renderer.py`** - Image processing
- **`model_loader.py`** - ML model loading
- **`ocr_fallback.py`** - OCR fallback strategies

#### Models (`/backend/app/models/`)
- **`requests.py`** - Pydantic request models
- **`responses.py`** - Pydantic response models

#### Utils (`/backend/app/utils/`)
- **`memory_guard.py`** - Memory usage monitoring

### Configuration
- **`requirements.txt`** - Python dependencies
  - fastapi, uvicorn
  - snowflake-connector-python
  - pydantic

- **`.env`** - Environment variables (gitignored)
- **`.env.example`** - Environment template
  ```
  SNOWFLAKE_ACCOUNT=...
  SNOWFLAKE_USER=...
  SNOWFLAKE_PASSWORD=...
  SNOWFLAKE_DATABASE=...
  SNOWFLAKE_SCHEMA=...
  SNOWFLAKE_WAREHOUSE=...
  ```

### Testing
- **`test_snowflake_quick.py`** - Quick Snowflake connection test
- **`test_snowflake_integration.py`** - Full integration tests
- **`test_structure.py`** - Project structure validation
- **`test_phase1.py`** - Phase 1 feature tests
- **`test_deepseek.py`** - DeepSeek integration tests

### Documentation
- **`DEEPSEEK_README.md`** - DeepSeek OCR integration guide

---

## Slack Listener Service

**Port:** 3003
**Purpose:** Receive Slack slash commands and forward to Postman Flow
**Location:** `/slack-listener/`

### Key Files
- **`index.js`** - Express server for Slack webhooks
  - Receives `/impact` commands
  - Forwards to Postman Action URL
  - Immediate acknowledgment to Slack

- **`package.json`** - Dependencies (express, axios)
- **`.env`** - Configuration (gitignored)
- **`.env.example`** - Environment template
  ```
  PORT=3003
  POSTMAN_ACTION_URL=https://...
  SLACK_SIGNING_SECRET=...
  ```

- **`.gitignore`** - Excludes node_modules, .env

### Documentation
- **`README.md`** - Setup and deployment guide

### Slack Integration
- Slash command: `/impact "feature request"`
- Response: Immediate 200 OK
- Background: Triggers Postman Flow

---

## Snowflake Integration

**Purpose:** Data warehousing + Cortex LLM for cost savings
**Location:** `/snowflake/`

### SQL Scripts

#### Setup
- **`setup_tables.sql`** - Create database schema
  - Tables: PR_GENERATIONS, COMMITS, FILES
  - Indexes and constraints

- **`fix_commits_table.sql`** - Schema migration/fixes

#### Data Population
- **`populate_data_NO_COMMITS.sql`** - Sample data without commits
- **`populate_perfect_data.sql`** - Full sample dataset

#### Execution
- **`FINAL_RUN_THIS.sql`** - Master setup script
  - Runs all setup steps in order
  - Creates schema and populates data

#### Configuration
- **`cortex_analyst_semantic_model.yaml`** - Cortex Analyst semantic model
  - Table definitions
  - Relationships
  - Business metrics

### Documentation
- **`README.md`** - Snowflake setup and usage guide

---

## Demo Resources

**Location:** `/demo/`

### Files
- **`README.md`** - Demo scenario walkthrough
  - Live demo script
  - Judge-clickable proof points

- **`HYBRID_AI_DEMO_SCENARIO.md`** - Hybrid AI architecture demo
  - Postman AI Agent orchestration
  - Claude for code generation
  - Snowflake Cortex for cost optimization

- **`SNOWFLAKE_SHOWCASE.sql`** - SQL queries for demo
  - Analytics examples
  - Cortex LLM queries

- **`snowflake-pr-generations-table.sql`** - PR_GENERATIONS table schema

---

## Mock Repository

**Purpose:** Test repository for code search demos
**Location:** `/mock-repo/postman-api-toolkit/`

### Structure
- **`server.js`** - Express API server
- **`package.json`** - Dependencies

#### Routes (`/routes/`)
- **`health.js`** - Health check endpoint
- **`users.js`** - User management API
- **`echo.js`** - Echo test endpoint

#### Middleware (`/middleware/`)
- **`logger.js`** - Request logging middleware

#### Documentation (`/docs/`)
- **`API.md`** - API documentation

### Configuration
- **`README.md`** - Mock repo overview
- **`.gitignore`** - Standard Node.js exclusions
- **`SETUP.md`** - Setup instructions (in `/mock-repo/`)

---

## Scripts & Utilities

### Service Management
- **`start-all.sh`** - Start all services (ripgrep, dashboard, frontend, slack)
  - Runs in background with logging
  - PID tracking

- **`stop-all.sh`** - Stop all services
  - Kills all background processes
  - Cleans up PIDs

- **`quick-restart.sh`** - Restart all services
  - Stops → Starts → Shows status

- **`test-dashboard.sh`** - Test dashboard API
  - Health checks
  - Sample data verification

### Usage
```bash
# Start everything
./start-all.sh

# Stop everything
./stop-all.sh

# Restart
./quick-restart.sh

# Test
./test-dashboard.sh
```

---

## Logs & Runtime

**Location:** `/logs/`

### Log Files
- **`ripgrep.log`** - Ripgrep API logs (stdout/stderr)
- **`frontend.log`** - Next.js dev server logs
- **`backend.log`** - FastAPI/Python logs
- **`slack-listener.log`** - Slack service logs

### Log Format
- Timestamps
- Request/response data
- Error traces
- Service status

**Note:** All `.log` files are gitignored

---

## GitHub Actions

**Location:** `.github/workflows/`

### Workflows
- **`pm-copilot-monitor.yml`** - CI/CD pipeline
  - Runs on push to main
  - Tests all services
  - Deployment automation
  - Health monitoring

### Configuration
- Triggers: push, pull_request
- Jobs: test, build, deploy
- Secrets: GitHub environment secrets

---

## Quick Reference

### Port Assignments
| Service         | Port | Protocol |
|-----------------|------|----------|
| Ripgrep API     | 3001 | HTTP     |
| Dashboard API   | 3002 | HTTP     |
| Slack Listener  | 3003 | HTTP     |
| Frontend        | 3000 | HTTP     |
| Backend (Python)| 8000 | HTTP     |

### Key Environment Variables

#### Ripgrep API
```
PORT=3001
ALLOWED_ORIGINS=*
```

#### Postman
```
RIPGREP_API_URL=http://localhost:3001
CLAUDE_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
SLACK_WEBHOOK_PM=https://hooks.slack.com/...
REPO_OWNER=V-prajit
REPO_NAME=youareabsolutelyright
```

#### Snowflake
```
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
SNOWFLAKE_PASSWORD=...
SNOWFLAKE_DATABASE=PM_COPILOT
SNOWFLAKE_SCHEMA=PUBLIC
```

### Service Health Checks
```bash
# Ripgrep API
curl http://localhost:3001/api/health

# Dashboard API
curl http://localhost:3002/api/health

# Frontend
curl http://localhost:3000

# Check running services
lsof -i :3001,3002,3003,3000,8000
```

---

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Slack: /impact "Add dark mode toggle"                          │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│ Slack Listener (Port 3003)                                      │
│ - Validates request                                             │
│ - Forwards to Postman Action                                    │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│ Postman AI Agent (Orchestrator)                                 │
│ - Parses feature request                                        │
│ - Autonomous tool selection                                     │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
         ┌─────────┴─────────┐
         ↓                   ↓
┌────────────────┐  ┌─────────────────┐
│ Ripgrep API    │  │ GitHub API      │
│ (Port 3001)    │  │ - Get open PRs  │
│ - Search files │  │ - Check files   │
└────────┬───────┘  └─────────┬───────┘
         ↓                    ↓
         └──────────┬─────────┘
                    ↓
         ┌──────────────────────┐
         │ Claude API            │
         │ - Generate PR content │
         │ - Acceptance criteria │
         └──────────┬────────────┘
                    ↓
         ┌──────────────────────┐
         │ GitHub API            │
         │ - Create branch       │
         │ - Create PR           │
         └──────────┬────────────┘
                    ↓
         ┌──────────────────────┐
         │ Slack Webhook         │
         │ - Send notification   │
         │ - Show reasoning      │
         └──────────┬────────────┘
                    ↓
         ┌──────────────────────┐
         │ Dashboard API         │
         │ (Port 3002)           │
         │ - Store analytics     │
         └──────────┬────────────┘
                    ↓
         ┌──────────────────────┐
         │ Frontend Dashboard    │
         │ (Port 3000)           │
         │ - Visualize data      │
         └───────────────────────┘
```

---

## File Count Summary

| Directory           | Files | Purpose                          |
|---------------------|-------|----------------------------------|
| `/postman/`         | ~25   | Flow modules, collections, env   |
| `/ripgrep-api/`     | ~8    | Code search service              |
| `/dashboard-api/`   | ~6    | Analytics backend                |
| `/frontend/`        | ~20   | Next.js dashboard UI             |
| `/backend/`         | ~30   | Python/Snowflake integration     |
| `/slack-listener/`  | ~6    | Slack webhook receiver           |
| `/snowflake/`       | ~7    | SQL setup scripts                |
| `/docs/`            | ~200+ | Documentation (incl. Postman)    |
| `/demo/`            | ~4    | Demo scripts and scenarios       |
| `/mock-repo/`       | ~10   | Test repository                  |
| Root                | ~15   | Config, docs, scripts            |

**Total:** ~350+ files (excluding node_modules, .next, .git)

---

## Technology Dependencies

### Node.js Services
- **Express.js** - Web framework (ripgrep, dashboard, slack)
- **Axios** - HTTP client
- **CORS** - Cross-origin requests
- **dotenv** - Environment variables
- **@vscode/ripgrep** - Code search binary

### Python Backend
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Snowflake Connector** - Database driver
- **Pydantic** - Data validation

### Frontend
- **Next.js 16** - React framework (App Router)
- **React 19** - UI library
- **Tailwind CSS** - Styling
- **TypeScript** - Type safety

### External APIs
- **Claude API** (Anthropic Sonnet 4.5) - PR generation
- **GitHub REST API** - PR creation, file management
- **Slack Webhooks** - Team notifications
- **Snowflake Cortex** - LLM + data warehouse

---

## Git Repository Structure

### Main Branch
- **`main`** - Production-ready code
- **`temp`** - Current working branch

### Recent Commits
```
4e0a36d - Consolidated the documentation
3d05eac - Working dashboard and stuff
f732619 - Fixed the automation
513d6b8 - Working base stable
6b36793 - Add health monitoring features
```

### Ignored Files (`.gitignore`)
- `node_modules/`
- `.next/`
- `.env`, `.env.local`
- `*.log`
- `__pycache__/`, `*.pyc`
- `package-lock.json` (in some directories)

---

## Navigation Tips

### Finding Files Quickly

**By Feature:**
- AI Agent setup → `/postman/AI-AGENT-CONFIGURATION.md`
- Code search → `/ripgrep-api/src/services/ripgrep.js`
- PR generation → `/postman/modules/claude-generate-pr-module.json`
- Dashboard UI → `/frontend/app/dashboard/page.tsx`
- Snowflake queries → `/snowflake/FINAL_RUN_THIS.sql`

**By File Type:**
- **Configuration:** `.env`, `package.json`, `tsconfig.json`
- **Documentation:** `README.md`, `*.md` in `/docs/`
- **Source Code:** `/src/` directories, `app/` for Next.js
- **Tests:** `test*.py`, `test*.js`
- **Scripts:** `*.sh` in root

**By Service:**
- Ripgrep API → `/ripgrep-api/src/`
- Dashboard API → `/dashboard-api/src/`
- Frontend → `/frontend/app/`
- Backend → `/backend/app/`
- Slack → `/slack-listener/`

---

## Development Workflow

### Initial Setup
1. Read `SETUP.md` for full setup instructions
2. Copy `.env.example` → `.env` in each service directory
3. Run `npm install` in Node.js services
4. Run `pip install -r requirements.txt` in backend

### Daily Development
1. Start services: `./start-all.sh`
2. Check logs: `tail -f logs/*.log`
3. Make changes in relevant service directory
4. Test endpoints via Postman collections
5. Stop services: `./stop-all.sh`

### Adding New Features
1. Create Flow Module in `/postman/modules/`
2. Update AI Agent prompt in `/postman/AI-AGENT-CONFIGURATION.md`
3. Add collection in `/postman/collections/`
4. Update this index file
5. Document in `CLAUDE.md`

---

## Troubleshooting Reference

### Common Issues

**Port Conflicts:**
- Check: `lsof -i :3001,3002,3003,3000,8000`
- Fix: Update PORT in `.env` files

**404 Errors:**
- Verify URL paths (e.g., `/api/search` not `/search`)
- Check service is running: `curl http://localhost:{PORT}/api/health`

**Postman 422 Errors:**
- Add `Content-Type: application/json` header
- See: `docs/POSTMAN_FLOW_FIX_GUIDE.md`

**Missing Environment Variables:**
- Check `.env` files exist (not just `.env.example`)
- Verify Postman environment is selected
- See: `SETUP.md` for required variables

### Debug Commands
```bash
# Check all services
lsof -i :3001,3002,3003,3000,8000

# Test Ripgrep API
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"import"}'

# View logs
tail -f logs/ripgrep.log
tail -f logs/frontend.log

# Restart everything
./quick-restart.sh
```

---

## Future Roadmap

### Phase 2 (Planned)
- Calendar + Slack Bot for engineer availability
- Co-change analysis for better file detection
- Historical conflict pattern learning

### Phase 3 (Planned)
- Asana/Jira integration
- Automatic task creation and linking
- Code ownership-based assignment

### Phase 4 (Planned)
- DeepSeek OCR for large diffs
- CodeRabbit automated review
- Multi-model routing optimization

---

## Contributing

### Code Style
- **JavaScript:** ES6+, Express patterns
- **Python:** PEP 8, FastAPI async/await
- **React:** Functional components, hooks
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/)

### Pull Request Process
1. Create feature branch: `feature/feature-name`
2. Update documentation
3. Add tests if applicable
4. Run health checks
5. Submit PR to `main`

---

## License

MIT License - See LICENSE file (if exists)

---

## Support Resources

### Documentation
- `CLAUDE.md` - Main developer guide
- `SETUP.md` - Setup instructions
- `docs/` - Detailed guides
- `README.md` - Project overview

### External Resources
- [Postman Flows Docs](https://learning.postman.com/docs/postman-flows/)
- [Claude API Docs](https://docs.claude.com/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Slack Block Kit](https://docs.slack.dev/block-kit/)

---

**Built for Postman + Cal Hacks 12.0 - January 2025**

**Index Last Updated:** 2025-10-28
**Maintainer:** Project Team
**Repository:** youareabsolutelyright
