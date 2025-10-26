# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ First Time Setup - Important!

**Before editing this file**, run this command to keep your local changes private:
```bash
git update-index --assume-unchanged CLAUDE.md
```

This allows you to customize CLAUDE.md for your needs without affecting the shared version. Your edits will stay local and won't be committed to the repository.

To later update the shared version (if needed):
```bash
git update-index --no-assume-unchanged CLAUDE.md
```

## Recent Updates (2025-10-26)

### 🎉 HYBRID AI IMPLEMENTATION COMPLETE!

**Status: Backend Complete - Ready for Postman Flow Integration**

## ✅ What's Working (TESTED & VERIFIED):

### Backend Infrastructure
- ✅ **Snowflake Cortex Integration** - FULLY OPERATIONAL!
  - Connected to Snowflake account: MFFKJKS-EXB19493
  - Database: BUGREWIND, Schema: GIT_ANALYSIS
  - PR_GENERATIONS table created with sample data
  - Endpoint: `POST /api/snowflake/generate-pr` (TESTED with curl)
  - Response time: ~17 seconds, generates complete PR with code!

- ✅ **Backend API** (Port 8000)
  - Running: `python run.py` in backend/
  - Health check: http://localhost:8000/health
  - Snowflake health: http://localhost:8000/api/snowflake/health
  - All dependencies installed (snowflake-connector-python==3.6.0)

- ✅ **Ripgrep API** (Port 3001) - **PORT FIXED!**
  - Running: `npm run dev` in ripgrep-api/
  - Health check: http://localhost:3001/api/health
  - Search endpoint: POST /api/search
  - `.env` fixed to use PORT=3001 (was conflicting with backend on 8000)

### Postman Status
- ✅ Collections imported (6 modules available)
- ✅ Environment configured with all variables
- ✅ Existing flow has "Claude post" block that needs URL change
- ⏳ **NEXT**: Replace Claude API URL with Snowflake Cortex URL in existing flow

## 🔧 Critical Configuration:

### Environment Variables (.env files)
**Backend** (`backend/.env`):
```env
SNOWFLAKE_ACCOUNT=MFFKJKS-EXB19493
SNOWFLAKE_USER=RXH3770
SNOWFLAKE_PASSWORD=Rabib12345678@
SNOWFLAKE_DATABASE=BUGREWIND
SNOWFLAKE_SCHEMA=GIT_ANALYSIS
SNOWFLAKE_WAREHOUSE=BUGREWIND_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN
ENABLE_SNOWFLAKE=true
ENABLE_CORTEX_LLM=true
```

**Ripgrep API** (`ripgrep-api/.env`):
```env
PORT=3001  # IMPORTANT: Changed from 8000 to avoid conflict!
```

### Postman Flow - Required Changes
**In existing "Claude post" block:**
1. Change URL from Postman Cortex to: `http://localhost:8000/api/snowflake/generate-pr`
2. Update request body to Snowflake format:
```json
{
  "feature_request": "{{Start.body.text}}",
  "impacted_files": ["src/pages/Login.tsx"],
  "is_new_feature": false,
  "repo_name": "V-prajit/youareabsolutelyright"
}
```
3. Headers: Keep only `Content-Type: application/json`
4. Update Ripgrep block URL to: `http://localhost:3001/search` (was using wrong port)

## 🎯 NEXT IMMEDIATE STEPS:

1. **Start Both Services** (in separate terminals):
```bash
# Terminal 1: Backend (Snowflake)
cd backend && python run.py

# Terminal 2: Ripgrep
cd ripgrep-api && npm run dev
```

2. **Fix Postman Flow**:
   - Open existing flow: "Search using RIPGREP API and process AI responses"
   - Fix RIPGREP block URL: Change to `http://localhost:3001/search`
   - Fix Claude block: Replace with Snowflake Cortex endpoint
   - Test the flow!

3. **Deploy & Demo**:
   - Once flow works, deploy as Postman Action
   - Record 3-minute demo video
   - Showcase Hybrid AI: "Postman orchestrates, Snowflake Cortex generates"

## 📊 Demo Talking Points:

**Hybrid AI Architecture:**
- Postman Flow = Orchestration brain (sequential workflow)
- Snowflake Cortex (Mistral-Large) = Code generation brain
- Result: 30 seconds from Slack to GitHub PR

**Snowflake Value:**
- Cortex LLM built-in (no external AI API)
- All PR generations stored in data warehouse
- Cost efficient: ~$0.001 vs $0.015 per generation
- Time Travel queries, semantic search ready

## 🐛 Known Issues & Solutions:

**Issue**: Both services on port 8000
**Solution**: Changed Ripgrep to port 3001 in `.env` ✅

**Issue**: Postman Flow shows 404 on Ripgrep
**Solution**: Update Ripgrep block URL to `http://localhost:3001/search`

**Issue**: Claude API giving 400 Bad Request
**Solution**: Replace with Snowflake endpoint + hardcode test values for now

## 📁 Key Files Updated This Session:

- `backend/.env` - Added Snowflake credentials
- `backend/app/routes/snowflake.py` - Added `/generate-pr` endpoint
- `backend/app/services/snowflake_service.py` - Added `generate_pr_with_cortex()` method
- `backend/app/models/requests.py` - Added `GeneratePRRequest` model
- `ripgrep-api/.env` - **Changed PORT from 8000 to 3001**
- `demo/snowflake-pr-generations-table.sql` - Database setup
- `demo/HYBRID_AI_DEMO_SCENARIO.md` - 3-minute demo script
- `demo/SNOWFLAKE_SHOWCASE.sql` - Demo queries for judges
- `postman/collections/snowflake-generate-pr.json` - New collection

---

### ✅ New Feature Handling Implementation

**What Changed:**
- Ripgrep API now handles "new feature" requests (when no existing files are found)
- Returns structured response with `is_new_feature` flag and helpful context
- Claude API prompt updated to create new files OR modify existing ones
- No Postman Flow changes required - just update Claude prompt
- Comprehensive documentation added: `/docs/POSTMAN_FLOW_NEW_FEATURES.md`

**Testing:**
- ✅ New feature test: `{"text": "add oauth"}` → Returns `is_new_feature: true`, empty files array
- ✅ Existing feature test: `{"text": "update search"}` → Returns file paths, `is_new_feature: false`

**Files Modified:**
- `ripgrep-api/src/routes/search.js:48-67` - Added new feature detection
- `docs/POSTMAN_FLOW_NEW_FEATURES.md` - Complete setup guide

---

## Project Overview

**"You Are Absolutely Right"** is a **PM Copilot** that transforms vague product specifications into actionable engineering tasks with **receipts, impact analysis, and tiny PRs**—all from a single Slack command.

### The Problem We Solve

Vague PM sentences waste engineering cycles because someone has to:
- Translate fuzzy requirements into acceptance criteria
- Figure out which code files need to change
- Create GitHub PRs with proper context
- Push work through project management tools

**Our solution makes this loop automatic, auditable, and judge-clickable.**

### How It Works (End-to-End)

1. **PM speaks in Slack**: `/impact "Add ProfileCard to /users"`
2. **Postman Flow** (deployed as an Action URL) receives the webhook
3. **AI Agent block** parses the natural language intent and plans the workflow
4. **Ripgrep API** finds relevant code files based on the feature description
5. **Mock server** provides test data for validation
6. **Claude API** drafts a ≤30-line patch + acceptance criteria
7. **GitHub API** creates a PR with the patch
8. **Slack webhook** notifies PM and engineer with structured Block Kit message
9. **Output**: Intent, acceptance criteria, impacted files, PR link, risk assessment

### Why This Wins Hackathons

**Postman Judging Criteria Alignment:**
- **Use of Postman Technology (20%)**: AI Agent block, deployed Actions, Mock servers, Flow modules, HTTP blocks
- **Multi-API Orchestration**: 4+ APIs (Ripgrep, Claude, GitHub, Slack)
- **Functionality (25%)**: Multi-step reasoning, real-time decision making
- **Real-World Impact (20%)**: Solves PM→Engineer handoff friction
- **Innovation (20%)**: "Receipts-first" design with code citations
- **UX/Presentation (15%)**: Slack Block Kit, clear demo, structured JSON output

**Optional Bonus Points:**
- Agentverse/ASI:One registration (Chat Protocol for agent discovery)
- Elastic MCP server integration (future enhancement)
- CodeRabbit AI review attachment (post-PR polish)

## MVP Architecture (Postman-First)

```
┌─────────────────────────────────────────────────────────────┐
│  PM in Slack: /impact "Add ProfileCard to /users"          │
└────────────────────┬────────────────────────────────────────┘
                     │ POST webhook
                     ▼
         ┌───────────────────────────┐
         │  Postman Action (Cloud)   │
         │  • Public URL endpoint    │
         │  • Receives webhook data  │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  AI Agent Block           │
         │  • Parse PM intent        │
         │  • Plan workflow steps    │
         │  • Decide API calls       │
         └───────────┬───────────────┘
                     │
         ┌───────────┴────────────────────────────────────┐
         │                                                │
         ▼                                                ▼
    ┌─────────────────┐                        ┌──────────────────┐
    │ HTTP: Ripgrep   │                        │ Mock Server      │
    │ • Search code   │                        │ • Test data      │
    │ • Find files    │                        │ • Sample output  │
    └────────┬────────┘                        └────────┬─────────┘
             │                                          │
             └────────────┬─────────────────────────────┘
                          ▼
              ┌───────────────────────┐
              │  AI Agent / HTTP      │
              │  • Claude API call    │
              │  • Generate PR draft  │
              │  • Acceptance criteria│
              └───────────┬───────────┘
                          │
         ┌────────────────┴──────────────────┐
         │                                   │
         ▼                                   ▼
    ┌─────────────────┐            ┌─────────────────┐
    │ HTTP: GitHub    │            │ HTTP: Slack     │
    │ • Create PR     │            │ • Notify PM     │
    │ • Add labels    │            │ • Notify Eng    │
    └─────────────────┘            └─────────────────┘
```

## Tech Stack

### Core Technologies (MVP)

**Postman Flows**
- **AI Agent Block**: GPT-5 powered reasoning and planning
- **HTTP Request Blocks**: Multi-API orchestration
- **Actions**: Deploy flow as public URL endpoint (Postman v11.42.3+)
- **Mock Servers**: Test data generation and validation
- **Flow Modules**: Reusable workflow components
- **Analytics**: Tool call logging and system prompt visibility

**APIs Integrated (Multi-API Requirement)**
1. **Ripgrep API**: Code search and file discovery
2. **Claude API**: PR generation and acceptance criteria drafting
3. **GitHub REST API**: Pull request creation
4. **Slack Incoming Webhooks**: Notifications and Block Kit messages

**Optional Technologies**
- **Frontend**: Next.js 16.0.0 (App Router) for dashboard/demo
- **Node.js**: Ripgrep API wrapper service
- **TypeScript**: v5 with strict mode

### Future Enhancements (Post-MVP)

**Elastic Stack**
- **Elasticsearch Serverless**: Advanced code indexing and co-change analysis
- **ES|QL**: Owner discovery and impact set computation
- **Graph Explore**: Visual "Git Causality Map"
- **Agent Builder MCP**: Expose search tools to AI agents

**Project Management**
- **Asana API**: Automated task creation with checklist
- **Jira API**: Alternative task tracking integration

**Advanced Features**
- **DeepSeek-OCR Visual Compression**: Render large diffs as images (10-40x token reduction)
- **CodeRabbit**: Automated AI code review
- **Agentverse/ASI:One**: Chat Protocol registration for agent discovery

## Development Commands

### Ripgrep API Service (Node.js)
```bash
cd ripgrep-api
npm install
npm run dev      # Development server on http://localhost:3001
npm run build    # Production build
npm start        # Production server
```

**Setup** (if needed):
```bash
cd ripgrep-api
npm init -y
npm install express ripgrep-js cors dotenv
```

### Frontend (Optional Dashboard)
```bash
cd frontend
npm install
npm run dev      # Development server on http://localhost:3000
npm run build    # Production build
npm start        # Production server
```

### Postman Flows
- Open Postman Desktop (v11.42.3+)
- Import `postman/pm-copilot-flow.json`
- Deploy as Action to get public URL
- Configure environment variables in Postman

## Configuration & Environment

### Postman Environment Variables
Configure in Postman Flows environment:
- `RIPGREP_API_URL`: Ripgrep API endpoint (e.g., http://localhost:3001)
- `CLAUDE_API_KEY`: Anthropic Claude API key
- `GITHUB_TOKEN`: GitHub personal access token (with `repo` scope)
- `SLACK_WEBHOOK_PM`: Slack incoming webhook for PM notifications
- `SLACK_WEBHOOK_ENG`: Slack incoming webhook for engineer notifications
- `REPO_OWNER`: Default GitHub repository owner
- `REPO_NAME`: Default GitHub repository name

### Ripgrep API Environment Variables
Located in `ripgrep-api/.env` (see `ripgrep-api/.env.example`):
- `PORT`: Server port (default: 3001)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: *)
- `MAX_SEARCH_RESULTS`: Maximum search results (default: 50)

### Frontend Environment Variables (Optional)
Located in `frontend/.env.local`:
- `NEXT_PUBLIC_POSTMAN_ACTION_URL`: Postman Action public URL
- `NEXT_PUBLIC_API_URL`: Backend API URL (if needed)

**Note**: Frontend variables must use `NEXT_PUBLIC_` prefix to be accessible in browser.

### Slack App Configuration

**Required Slack App Setup:**
1. Create a Slack App at api.slack.com/apps
2. Enable **Incoming Webhooks**
3. Add webhook URLs to Postman environment
4. Optional: Enable **Slash Commands** for `/impact` command
5. Configure **Request URL** to point to Postman Action URL

**Slash Command Configuration:**
- Command: `/impact`
- Request URL: `{your-postman-action-url}`
- Short Description: "Generate PR from PM spec"
- Usage Hint: `[feature description]`

**Required Scopes:**
- `incoming-webhook`
- `commands` (if using slash commands)

## Project Structure

```
youareabsolutelyright/
├── postman/                    # Postman Flows and collections
│   ├── pm-copilot-flow.json   # Main flow (AI Agent orchestration)
│   ├── ripgrep-collection.json # Ripgrep API requests
│   ├── github-collection.json  # GitHub API requests
│   ├── slack-collection.json   # Slack webhook requests
│   ├── mock-servers/          # Mock server definitions
│   │   └── test-data.json     # Sample test data responses
│   └── README.md              # Postman workspace setup guide
│
├── ripgrep-api/               # Ripgrep API wrapper (Node.js)
│   ├── src/
│   │   ├── index.js          # Express server
│   │   ├── routes/
│   │   │   └── search.js     # Search endpoint
│   │   └── services/
│   │       └── ripgrep.js    # Ripgrep integration
│   ├── package.json
│   ├── .env.example
│   └── README.md
│
├── frontend/                  # Optional Next.js dashboard
│   ├── app/
│   │   ├── page.tsx          # Home page (PR history)
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css       # Global styles
│   ├── components/           # React components
│   │   ├── ImpactViewer.tsx # Impact set visualization
│   │   └── PRCard.tsx       # PR preview card
│   ├── package.json
│   └── tsconfig.json
│
├── docs/                           # Documentation and demo materials
│   ├── DEMO_SCRIPT.md             # Demo script for judges
│   ├── API_EXAMPLES.md            # API request/response examples
│   ├── SETUP.md                   # Setup and configuration guide
│   ├── POSTMAN_FLOW_NEW_FEATURES.md  # NEW: Handling new features guide
│   ├── screenshots/               # UI screenshots
│   └── videos/                    # Demo video links
│
├── CLAUDE.md                # This file
└── README.md                # Public-facing README
```

## Postman Flows Implementation

### Flow Structure

**1. Start Block (Webhook Trigger)**
- Type: `Request-triggered Action`
- Input: `{ "text": "Add ProfileCard to /users", "user_id": "@engineer" }`
- Output: Structured JSON to AI Agent

**2. AI Agent Block (Planning & Reasoning)**
- Model: GPT-5 (default as of 2025)
- Prompt:
  ```
  You are a PM Copilot. Parse the feature request and extract:
  1. Feature name
  2. Target files/routes to modify
  3. Keywords for code search
  4. Acceptance criteria (3-5 bullet points)

  Input: {workflow.text}
  Output format: JSON with keys [feature_name, search_keywords, acceptance_criteria, target_route]
  ```
- Tools: HTTP blocks (auto-invoked as needed)
- Output: Structured plan for downstream blocks

**3. HTTP Block → Ripgrep API**
- Method: POST
- URL: `{{RIPGREP_API_URL}}/search`
- Body:
  ```json
  {
    "query": "{{ai_agent.search_keywords}}",
    "path": "src/",
    "type": "tsx"
  }
  ```
- Output: `{ "files": ["src/components/UserProfile.tsx", ...], "matches": [...] }`

**4. Mock Server Block (Test Data)**
- Purpose: Provide sample code snippets for validation
- Returns: Mock file contents, sample test cases
- Used for: Demonstrating "test-driven" PR generation

**5. HTTP Block → Claude API (PR Generation)**
- Method: POST
- URL: `https://api.anthropic.com/v1/messages`
- Headers:
  ```
  x-api-key: {{CLAUDE_API_KEY}}
  anthropic-version: 2023-06-01
  content-type: application/json
  ```
- Body (Updated for New Feature Handling):
  ```json
  {
    "model": "claude-sonnet-4.5-20250929",
    "max_tokens": 4000,
    "messages": [
      {
        "role": "user",
        "content": "You are a senior engineer working on a codebase.

Feature Request: {{Start.text}}

Search Results from Ripgrep:
{{RIPGREP_API.body.data.message}}

Files Found: {{RIPGREP_API.body.data.total}}
{{#each RIPGREP_API.body.data.files}}
- {{this}}
{{/each}}

IMPORTANT INSTRUCTIONS:
- If no files were found (total = 0), this is a NEW FEATURE. You should create new files and suggest a file structure.
- If files were found, modify those existing files with a ≤30-line patch.

For NEW features, provide:
1. PR Title
2. List of new files to create (with paths)
3. Code for each file
4. Acceptance criteria (3-5 bullets)
5. Integration instructions

For EXISTING features, provide:
1. PR Title
2. Changes to each file (code patches)
3. Acceptance criteria (3-5 bullets)

Use TypeScript and React 19. Keep total changes ≤30 lines."
      }
    ]
  }
  ```
- Output: Claude's response with PR content in `body.content[0].text`

**6. HTTP Block → GitHub API (Create PR)**
- Method: POST
- URL: `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls`
- Headers:
  ```
  Authorization: Bearer {{GITHUB_TOKEN}}
  Accept: application/vnd.github+json
  X-GitHub-Api-Version: 2022-11-28
  ```
- Body:
  ```json
  {
    "title": "{{claude.pr_title}}",
    "body": "{{claude.pr_body}}\n\n## Acceptance Criteria\n{{ai_agent.acceptance_criteria}}\n\n## Impacted Files\n{{ripgrep.files}}",
    "head": "feature/{{ai_agent.feature_name}}",
    "base": "main"
  }
  ```
- Output: `{ "html_url": "https://github.com/.../pull/123", "number": 123 }`

**7. HTTP Block → Slack Webhook (Notify PM & Engineer)**
- Method: POST
- URL: `{{SLACK_WEBHOOK_PM}}`
- Body (Block Kit):
  ```json
  {
    "blocks": [
      {
        "type": "header",
        "text": {
          "type": "plain_text",
          "text": "✅ PR Created"
        }
      },
      {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": "*Feature:*\n{{Start.text}}"
          },
          {
            "type": "mrkdwn",
            "text": "*PR Number:*\n#{{HTTP Request.body.number}}"
          }
        ]
      },
      {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": "*Files Changed:*\n{{RIPGREP API.body.data.total}}"
          },
          {
            "type": "mrkdwn",
            "text": "*Is New Feature:*\n{{RIPGREP API.body.data.is_new_feature}}"
          }
        ]
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Impacted Files:*\n{{#each RIPGREP API.body.data.files}}- `{{this}}`\n{{/each}}{{#if RIPGREP API.body.data.is_new_feature}}_New files will be created_{{/if}}"
        }
      },
      {
        "type": "actions",
        "elements": [
          {
            "type": "button",
            "text": {
              "type": "plain_text",
              "text": "View PR"
            },
            "url": "{{HTTP Request.body.html_url}}",
            "style": "primary"
          }
        ]
      }
    ]
  }
  ```

**Important Variable Paths:**
- `{{Start.text}}` - Original feature request
- `{{RIPGREP API.body.data.total}}` - Number of files found
- `{{RIPGREP API.body.data.is_new_feature}}` - Boolean flag
- `{{RIPGREP API.body.data.files}}` - Array of file paths
- `{{HTTP Request.body.html_url}}` - GitHub PR URL (from GitHub API response)
- `{{HTTP Request.body.number}}` - PR number

**Note:** Replace `HTTP Request` with your actual GitHub block name in Postman Flow.

**8. Response Block**
- Returns final JSON to Action caller:
  ```json
  {
    "success": true,
    "pr_url": "{{github.html_url}}",
    "impacted_files": "{{ripgrep.files}}",
    "acceptance_criteria": "{{ai_agent.acceptance_criteria}}"
  }
  ```

### Flow Analytics & Logging

Postman Flows automatically logs:
- Tool call information (which HTTP blocks were invoked)
- System prompts used by AI Agent
- Response times for each block
- Error traces for debugging

**Access via**: Postman Flows → Analytics tab

### Error Handling

**Resilience Patterns:**
1. **HTTP Block Timeouts**: Set 30s timeout on all external API calls
2. **Retry Logic**: Use Decision blocks to retry failed API calls (max 3 attempts)
3. **Fallback Responses**: Mock server provides fallback data if Ripgrep API is down
4. **Error Logging**: All errors logged to Flows Analytics
5. **Graceful Degradation**: If GitHub PR fails, still send Slack notification with patch

**Example Decision Block (Retry Logic):**
```
If HTTP.status != 200:
  → Retry (max 3x)
Else:
  → Continue to next block
```

### Handling New Features (Updated Implementation)

**Problem:** When PMs request completely new features (e.g., "add OAuth"), RIPGREP returns no files, which previously broke the Claude API call.

**Solution:** The Ripgrep API now returns a structured response with `is_new_feature` flag.

**How It Works:**

1. **RIPGREP API Response** includes:
   - `is_new_feature: true/false` - Boolean flag
   - `message` - Context for Claude
   - `files: []` - Empty array (not error message) when no files found

2. **Claude API Prompt** adapts based on context:
   - Reads the `message` field
   - Checks `total` count
   - Generates new file structure if `total = 0`
   - Modifies existing files if `total > 0`

3. **No Flow Changes Required** - Claude is smart enough to read the instructions and adapt

**Example Scenarios:**

**Scenario 1: New Feature ("add oauth")**
```json
// RIPGREP Response
{
  "data": {
    "files": [],
    "total": 0,
    "is_new_feature": true,
    "message": "No existing files found - may be a new feature..."
  }
}

// Claude receives context and creates:
// - src/auth/OAuthProvider.tsx
// - src/hooks/useOAuth.ts
// - Integration instructions
```

**Scenario 2: Existing Feature ("update ProfileCard")**
```json
// RIPGREP Response
{
  "data": {
    "files": ["src/components/ProfileCard.tsx"],
    "total": 1,
    "is_new_feature": false,
    "message": "Found existing files..."
  }
}

// Claude receives context and modifies:
// - src/components/ProfileCard.tsx (≤30 line patch)
```

**Testing:**
- New feature: `{"text": "add oauth"}` → Creates new files
- Existing feature: `{"text": "update search"}` → Modifies existing files

**Documentation:** See `/docs/POSTMAN_FLOW_NEW_FEATURES.md` for detailed setup guide.

## API Integration Details

### 1. Ripgrep API Wrapper

**Why We Need It:**
Ripgrep is a CLI tool, not an HTTP API. We wrap it in a simple Express.js service to make it accessible to Postman Flows.

**Endpoint**: `POST /search`

**Request:**
```json
{
  "query": "ProfileCard",
  "path": "src/",
  "type": "tsx",
  "case_sensitive": false
}
```

**Response (Existing Feature):**
```json
{
  "success": true,
  "data": {
    "files": [
      "src/components/ProfileCard.tsx",
      "src/pages/UserProfile.tsx"
    ],
    "matches": [
      {
        "file": "src/components/ProfileCard.tsx",
        "line": 15,
        "column": 13,
        "content": "export const ProfileCard = ({ user }) => {",
        "match_text": "ProfileCard"
      }
    ],
    "total": 2,
    "is_new_feature": false,
    "message": "Found existing files that may be related to this feature."
  },
  "query": {
    "pattern": "ProfileCard",
    "path": "src/",
    "type": "tsx",
    "case_sensitive": false
  }
}
```

**Response (New Feature - No Files Found):**
```json
{
  "success": true,
  "data": {
    "files": [],
    "matches": [],
    "total": 0,
    "is_new_feature": true,
    "message": "No existing files found - may be a new feature. Claude should create new files and suggest a file structure."
  },
  "query": {
    "pattern": "oauth",
    "path": "./",
    "type": "all",
    "case_sensitive": false
  }
}
```

**Implementation** (`ripgrep-api/src/routes/search.js`):
```javascript
router.post('/search', async (req, res) => {
  try {
    const { query, path, type, case_sensitive } = req.body;

    // Execute search
    const results = await search(query, {
      path: path || process.env.DEFAULT_SEARCH_PATH || './',
      type,
      case_sensitive: case_sensitive || false,
      max_results: parseInt(process.env.MAX_SEARCH_RESULTS || '50', 10),
    });

    // Determine if this is a new feature (no existing files)
    const isNewFeature = results.files.length === 0;

    res.json({
      success: true,
      data: {
        ...results,
        files: results.files,  // Keep as empty array if no files found
        is_new_feature: isNewFeature,
        message: isNewFeature
          ? 'No existing files found - may be a new feature. Claude should create new files and suggest a file structure.'
          : 'Found existing files that may be related to this feature.',
      },
      query: {
        pattern: query,
        path: path || './',
        type: type || 'all',
        case_sensitive: case_sensitive || false,
      },
    });
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});
```

**Key Features:**
- Returns `is_new_feature: true` when no files are found
- Keeps `files` as empty array `[]` instead of error message
- Provides helpful `message` for both scenarios
- Enables Postman Flow to handle new vs. existing features differently

**Alternative: MCP Ripgrep Server**
For advanced use cases, integrate the **Ripgrep MCP Server** (March 2025):
- Provides Model Context Protocol interface
- Compatible with Claude Desktop and other MCP clients
- Can be exposed as HTTP endpoint via MCP-to-REST bridge

### 2. Claude Messages API

**Endpoint**: `POST https://api.anthropic.com/v1/messages`

**Headers:**
```
x-api-key: {CLAUDE_API_KEY}
anthropic-version: 2023-06-01
content-type: application/json
```

**Request:**
```json
{
  "model": "claude-sonnet-4.5-20250929",
  "max_tokens": 4000,
  "messages": [
    {
      "role": "user",
      "content": "You are a senior engineer. Generate a ≤30-line PR patch that adds ProfileCard component to /users route. Use TypeScript and React 19. Include acceptance criteria."
    }
  ]
}
```

**Response:**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "# PR: Add ProfileCard to /users\n\n## Changes\n```tsx\n// src/pages/users.tsx\nimport { ProfileCard } from '@/components/ProfileCard';\n...\n```\n\n## Acceptance Criteria\n1. ProfileCard displays user avatar and name\n2. Route /users renders ProfileCard list\n3. Component has snapshot test coverage"
    }
  ]
}
```

**Why Claude?**
- Superior code generation quality
- Understands TypeScript/React patterns
- Can draft acceptance criteria in natural language
- Supports conversational context for iterative refinement

### 3. GitHub REST API

**Create Pull Request**: `POST /repos/{owner}/{repo}/pulls`

**Headers:**
```
Authorization: Bearer {GITHUB_TOKEN}
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

**Request:**
```json
{
  "title": "Add ProfileCard to /users route",
  "body": "## Summary\nAdds new ProfileCard component...\n\n## Acceptance Criteria\n- [ ] ProfileCard component created\n- [ ] /users route updated\n- [ ] Tests pass",
  "head": "feature/profile-card",
  "base": "main"
}
```

**Response:**
```json
{
  "id": 123456,
  "number": 42,
  "state": "open",
  "title": "Add ProfileCard to /users route",
  "html_url": "https://github.com/owner/repo/pull/42",
  "created_at": "2025-10-25T12:00:00Z"
}
```

**Note**: Branch must exist before creating PR. For MVP, assume branch exists or use GitHub's auto-branch creation feature.

### 4. Slack Incoming Webhooks

**Endpoint**: `POST {SLACK_WEBHOOK_URL}` (obtained from Slack App config)

**Request (Block Kit):**
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "✅ PR Created: Add ProfileCard to /users"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Feature:* ProfileCard component"
        },
        {
          "type": "mrkdwn",
          "text": "*Impacted Files:* 3"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Acceptance Criteria:*\n• ProfileCard displays avatar\n• /users route renders list\n• Snapshot tests pass"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View PR"
          },
          "url": "https://github.com/owner/repo/pull/42",
          "style": "primary"
        }
      ]
    }
  ]
}
```

**Response:** `200 OK` (Slack posts message to channel)

**Best Practices:**
- Use Block Kit for rich formatting
- Include actionable buttons (View PR, Approve, etc.)
- Keep messages concise (3-5 blocks max)
- Use emojis sparingly (✅, 🚀, ⚠️)

## Judging Criteria Alignment

### Functionality & Technical Implementation (25%)

**What We Demonstrate:**
- ✅ Multi-step reasoning via AI Agent block
- ✅ Successful API orchestration (4 APIs)
- ✅ Real-time decision making (parse intent → search code → generate PR)
- ✅ Error handling and retry logic
- ✅ End-to-end workflow (Slack → Postman → GitHub)

**Judge-Clickable Proof:**
- Live Postman Action URL (public endpoint)
- Sample input: `{ "text": "Add dark mode toggle", "user_id": "@alice" }`
- Sample output: JSON with PR URL, impacted files, acceptance criteria
- Flows Analytics showing tool call logs

### Use of Postman Technology (20%)

**Postman Features Utilized:**
- ✅ **AI Agent Block**: GPT-5 powered planning and reasoning
- ✅ **HTTP Request Blocks**: Multi-API calls (Ripgrep, Claude, GitHub, Slack)
- ✅ **Actions**: Deployed flow with public URL
- ✅ **Mock Servers**: Test data generation
- ✅ **Flow Modules**: Reusable components (error handling, retry logic)
- ✅ **Analytics**: Tool call logging and debugging
- ✅ **Collections**: Organized API requests for all integrations

**Optional Bonus Points:**
- ✅ **Agentverse/ASI:One Registration**: Implement Chat Protocol for agent discovery
  - Register agent on Agentverse
  - Enable Chat Protocol communication
  - Make agent discoverable via ASI:One

**How to Register on Agentverse (Optional):**
1. Sign up at agentverse.ai
2. Create API key at as1.ai
3. Implement Chat Protocol in Postman Flow
4. Register agent in Almanac
5. Configure for ASI:One integration

### Innovation & Creativity (20%)

**Novel Approach:**
- ✅ **"Receipts-first" design**: Every decision has code citations
- ✅ **Tiny PR constraint**: ≤30 lines keeps PRs reviewable and mergeable
- ✅ **Instant PM→Eng handoff**: Eliminates back-and-forth clarification cycles
- ✅ **Multi-modal reasoning**: Combines code search + AI generation + project management

**Unconventional Use of Tech:**
- Ripgrep (CLI tool) → Exposed as HTTP API for Postman Flows
- Slack Block Kit → Becomes PM's command center
- AI Agent → Acts as "PM translator" bridging human intent to code

### Real-World Impact & Usefulness (20%)

**Problem Solved:**
PM specifications are often vague ("Add a profile card"). Engineers waste hours:
1. Clarifying requirements with PMs
2. Searching codebase for relevant files
3. Drafting acceptance criteria
4. Creating boilerplate PRs

**Our Solution:**
- 🚀 **Speed**: 30 seconds from Slack message to GitHub PR
- 🎯 **Accuracy**: Code search finds exact files to modify
- 📋 **Clarity**: Auto-generated acceptance criteria
- 🔗 **Traceability**: Every decision has receipts (commit quotes, co-change scores)

**Who Benefits:**
- **PMs**: Communicate intent naturally, see instant results
- **Engineers**: Get precise tasks with context, not vague specs
- **Teams**: Reduce handoff friction, ship faster

### User Experience & Presentation (15%)

**Demo Flow (Judge-Ready):**
1. Show Slack message: `/impact "Add dark mode toggle to settings"`
2. 3-second wait...
3. Show Slack Block Kit response:
   - Feature: Dark mode toggle
   - Impacted files: `Settings.tsx`, `theme.ts`
   - Acceptance criteria (3 bullets)
   - [View PR] button
4. Click button → GitHub PR opens
5. Show Postman Flows Analytics → Tool call logs

**Presentation Quality:**
- ✅ Clean Slack UI (Block Kit formatting)
- ✅ Structured JSON output (easily parseable)
- ✅ Clear Postman Flow diagram (visual blocks + connections)
- ✅ Comprehensive README with setup instructions
- ✅ Demo video (< 3 minutes)

**Postman Workspace Setup:**
- Public workspace (no secrets exposed)
- README with:
  - What it does (1 paragraph)
  - APIs used (4 listed)
  - Setup instructions (env vars, dependencies)
  - Sample request/response
  - Demo video link

## Future Enhancements (Post-MVP)

### Phase 2: Elasticsearch Integration

**Replace Ripgrep API with Elastic Serverless:**
- **ES|QL**: Query commit history for co-change analysis
- **Graph Explore**: Visualize "Git Causality Map" (files that change together)
- **Agent Builder**: Expose Elastic tools via MCP server
- **Owner Discovery**: Find code owners based on commit history

**Impact Set with Receipts:**
Instead of just file names, return:
```json
{
  "files": ["Settings.tsx", "theme.ts"],
  "receipts": [
    {
      "file": "Settings.tsx",
      "co_change_score": 0.89,
      "commit_quote": "feat: Add theme switcher (#123)",
      "owner": "@alice"
    }
  ]
}
```

### Phase 3: Project Management Integration

**Asana API:**
- Create tasks with acceptance criteria as checklist
- Link back to GitHub PR
- Assign to engineer based on code ownership

**Jira API:**
- Alternative to Asana for teams using Jira
- Auto-populate story points based on PR size

### Phase 4: Visual Context Compression (DeepSeek-OCR)

**Problem:** Large diffs (1000+ lines) exceed Claude's context window.

**Solution:** Render diff as image → Send to Claude Vision API
- 5000-line diff = 4000 text tokens
- Same diff as 640x640 image = 100 vision tokens
- **97% token savings**

**Implementation:**
1. `diff-renderer` service: Converts git diff → PNG
2. Claude Vision API: Analyzes image, extracts bug origins
3. Return analysis with 90%+ cost reduction

**Tech Stack:**
- LaTeX or HTML-to-PNG pipeline
- Claude Sonnet 4.5 with vision support
- Optional: DeepSeek-OCR 3B local model for decompression

**References:**
- [DeepSeek-OCR Paper](https://arxiv.org/abs/2510.18234)
- [DeepSeek-OCR Model](https://huggingface.co/deepseek-ai/DeepSeek-OCR)

### Phase 5: Advanced Features

**CodeRabbit Integration:**
- Auto-attach AI code review to PRs
- Catch bugs before human review

**Frontend Dashboard:**
- View PR history
- Visualize impact sets
- Browse Git Causality Map
- Manage open tasks

**MLH Sponsor Prizes:**
- **.tech domain**: youareabsolutelyright.tech
- **DigitalOcean**: Host dashboard on DO App Platform
- **1Password**: Secure API key management

## Development Workflow

### Getting Started

**1. Clone Repository**
```bash
git clone https://github.com/yourusername/youareabsolutelyright.git
cd youareabsolutelyright
```

**2. Set Up Ripgrep API**
```bash
cd ripgrep-api
npm install
cp .env.example .env
# Edit .env with your configuration
npm run dev
```

**3. Import Postman Flow**
- Open Postman Desktop (v11.42.3+)
- Import `postman/pm-copilot-flow.json`
- Configure environment variables:
  - `RIPGREP_API_URL`: http://localhost:3001
  - `CLAUDE_API_KEY`: Your Anthropic API key
  - `GITHUB_TOKEN`: Your GitHub token
  - `SLACK_WEBHOOK_PM`: Your Slack webhook URL

**4. Deploy Postman Action**
- Click "Deploy" in Postman Flow
- Copy public URL (e.g., `https://flows-action.postman.com/abc123`)
- Configure Slack slash command to use this URL

**5. Test End-to-End**
```bash
# In Slack:
/impact "Add dark mode toggle to settings"

# Expected output:
# ✅ PR Created: Add dark mode toggle
# • Feature: Dark mode toggle
# • Impacted Files: 2
# • Acceptance Criteria: [...]
# [View PR] button
```

### Git Workflow
- Main branch: `main`
- Environment files (`.env`) are gitignored
- Postman collections exported to `postman/` directory
- Keep secrets in Postman environment variables (not committed)

### TypeScript Configuration (Optional Frontend)
- Strict mode enabled
- Target: ES2017
- JSX: react-jsx
- Module resolution: bundler
- Path aliases: `@/*` for imports

### Contribution Guidelines

**For Hackathon Teams:**
1. **Track A (Postman Lead)**: Build core flow, mock servers, API integrations
2. **Track B (Backend Dev)**: Ripgrep API wrapper, error handling, logging
3. **Track C (Demo/UX)**: Slack Block Kit formatting, demo video, README

**Quality Checklist:**
- [ ] All API calls have error handling
- [ ] Mock servers provide fallback data
- [ ] Flows Analytics shows tool call logs
- [ ] README has clear setup instructions
- [ ] Demo video < 3 minutes
- [ ] Public Postman workspace (no secrets)
- [ ] Sample input/output documented

## Deliverables for Judges

**Required:**
1. **Postman Action URL**: Public endpoint (e.g., `https://flows-action.postman.com/xyz`)
2. **Workspace Link**: Public Postman workspace with flow and collections
3. **README**: What it does, APIs used, setup instructions
4. **Sample Input/Output**:
   - Input: `{ "text": "Add ProfileCard to /users", "user_id": "@alice" }`
   - Output: `{ "pr_url": "...", "impacted_files": [...], "acceptance_criteria": [...] }`

**Bonus:**
5. **Demo Video**: < 3 minutes showing Slack → Postman → GitHub flow
6. **Agentverse Registration**: Chat Protocol enabled, agent discoverable
7. **Live Slack Integration**: Judges can test `/impact` command
8. **Frontend Dashboard**: Visual impact set viewer (optional)

## Resources

**Postman Documentation:**
- [AI Agent Block](https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/)
- [Deploy Flows as Actions](https://learning.postman.com/docs/postman-flows/build-flows/actions/)
- [Mock Servers](https://learning.postman.com/docs/design-apis/mock-apis/overview/)
- [Flows Analytics](https://learning.postman.com/docs/postman-flows/reference/flows-actions-overview/)

**API Documentation:**
- [Claude Messages API](https://docs.claude.com/en/api/messages)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Slack Block Kit](https://docs.slack.dev/block-kit/)
- [Ripgrep MCP Server](https://playbooks.com/mcp/mcollina-ripgrep)

**Agentverse/ASI:One:**
- [Create ASI:One Compatible Agent](https://docs.agentverse.ai/documentation/advanced-usages/asi-one-compatible-agent)
- [Agent Chat Protocol](https://docs.agentverse.ai/docs/uAgents/asimini-agent)

**Sponsor Prizes:**
- [.tech Domain (MLH)](https://get.tech/mlh)
- [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform)
- [CodeRabbit Integration](https://docs.coderabbit.ai/platforms/github-com)

---

## 🔧 Troubleshooting Guide (2025-10-26)

### Backend Server Issues

**Problem: Socket hangup on port 8000**
- **Solution**: Start backend using `python run.py` (not `python app/main.py`)
- **Command**:
  ```bash
  cd backend
  python run.py
  ```
- **Verify**: `curl http://localhost:8000/health`
- **Expected**: `{"status":"healthy","version":"1.0.0","service":"BugRewind API"}`

### Snowflake Cortex API Issues (422 Error)

**Problem: 422 Unprocessable Entity when calling `/api/snowflake/generate-pr`**
- **Cause**: Missing Content-Type header or incorrect JSON format in Postman Flow
- **Symptoms**: Backend logs show "Invalid HTTP request received", Postman shows 400/422 error
- **Solution**: See detailed fix guide at `/docs/POSTMAN_FLOW_FIX_GUIDE.md`

**Quick Fix Checklist:**
1. ✅ Add `Content-Type: application/json` header to "Claude post" HTTP block
2. ✅ Use `"query"` not `"text"` in RIPGREP API request body
3. ✅ Don't quote JSON arrays/booleans: `{{RIPGREP API.body.data.files}}` (no quotes)
4. ✅ Verify block names match variable paths exactly (case-sensitive)
5. ✅ Omit optional fields when empty (don't send empty string for `conflict_info`)

**Test Commands:**
```bash
# Test Snowflake endpoint directly
curl -X POST http://localhost:8000/api/snowflake/generate-pr \
  -H "Content-Type: application/json" \
  -d '{"feature_request":"test","impacted_files":[],"is_new_feature":true,"repo_name":"V-prajit/youareabsolutelyright"}'

# Expected: {"success":true,"pr_title":"...","pr_description":"...","branch_name":"..."}

# Test RIPGREP endpoint
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"import"}'

# Expected: {"success":true,"data":{"files":[...],"total":...,"is_new_feature":...}}
```

### Postman Flows Evaluate Block Issues

**Problem: "data is not defined" in Evaluate block**

The `data` object doesn't exist by default in Postman Flows Evaluate blocks. Use one of these approaches:

**Solution 1: Use Postman variable syntax (recommended)**
```javascript
const ripgrepFiles = {{RIPGREP API.body.data.files}} || [];
const prFiles = {{Get PR Files.body}} || [];
const pr = {{item}};

const prFilenames = prFiles.map(f => f.filename);

const overlapping = ripgrepFiles.filter(ripgrepFile =>
  prFilenames.some(prFile =>
    prFile.includes(ripgrepFile) || ripgrepFile.includes(prFile)
  )
);

const conflictScore = ripgrepFiles.length > 0
  ? Math.round((overlapping.length / ripgrepFiles.length) * 100)
  : 0;

({
  pr_number: pr.number,
  pr_title: pr.title,
  pr_url: pr.html_url,
  overlapping_files: overlapping,
  conflict_score: conflictScore,
  has_conflict: conflictScore > 0
})
```

**Solution 2: Define inputs explicitly**
- In Evaluate block UI, add inputs:
  - `ripgrepFiles` = `{{RIPGREP API.body.data.files}}`
  - `prFiles` = `{{Get PR Files.body}}`
  - `currentPR` = `{{item}}`
- Then reference them directly in code by name

**Problem: "return not in a function" error**
- **Solution**: Don't use explicit `return` statement
- **Instead**: Use parentheses around final object: `({ key: value })`

### Claude API Issues

**Problem: 404 Not Found when calling Claude API**
- **Cause**: Wrong URL (posting to `/` instead of `/v1/messages`)
- **Solution**: Update HTTP Request block:
  - URL: `https://api.anthropic.com/v1/messages`
  - Headers:
    ```
    x-api-key: {{CLAUDE_API_KEY}}
    anthropic-version: 2023-06-01
    content-type: application/json
    ```

### GitHub API Issues

**Problem: Get PR Files returns empty or fails**
- **Verify variables**:
  - `REPO_OWNER` = repository owner (e.g., "V-prajit")
  - `REPO_NAME` = repository name (e.g., "youareabsolutelyright")
  - `pr_number` = PR number from loop item
- **URL format**: `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls/{{pr_number}}/files`

### Quick Health Checks

```bash
# Backend server
curl http://localhost:8000/health

# RIPGREP server
curl http://localhost:3001/api/health

# Check running servers
lsof -ti:8000  # Backend
lsof -ti:3001  # RIPGREP

# Restart backend
cd backend && python run.py

# Restart RIPGREP
cd ripgrep-api && npm run dev

# Test RIPGREP API (correct)
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "import"}'

# Test Snowflake endpoint (correct)
curl -X POST http://localhost:8000/api/snowflake/generate-pr \
  -H "Content-Type: application/json" \
  -d '{"feature_request":"test feature","impacted_files":[],"is_new_feature":true,"repo_name":"V-prajit/youareabsolutelyright"}'
```

## License

MIT License - See LICENSE file for details
