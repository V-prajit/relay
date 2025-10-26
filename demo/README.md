# PM Copilot - Demo Setup Guide

## 🎯 Quick Start (15 Minutes to Working Demo)

This guide gets you from zero to a working Hybrid AI demo for hackathon presentation.

---

## Prerequisites

- [x] Postman Desktop (v11.42.3+)
- [x] Node.js 18+
- [x] Python 3.9+
- [x] Snowflake account (free trial works)
- [x] GitHub account with personal access token
- [x] Slack workspace with incoming webhook

---

## Step 1: Snowflake Setup (5 min)

### 1.1 Create Snowflake Account
1. Go to https://signup.snowflake.com/
2. Choose **30-day free trial**
3. Select **AWS** + **US East** region
4. Choose **Enterprise** edition (includes Cortex AI)

### 1.2 Run Setup SQL
1. Login to Snowflake web console
2. Open SQL worksheet
3. Copy contents of `demo/snowflake-pr-generations-table.sql`
4. Run all commands
5. Verify: `SELECT * FROM PR_GENERATIONS;`

### 1.3 Get Credentials
Note these values (you'll need them):
- **Account**: `abc12345.us-east-1` (from URL)
- **Username**: Your email
- **Password**: Your password

---

## Step 2: Backend Setup (3 min)

### 2.1 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2.2 Configure Environment
```bash
cp .env.example .env
# Edit .env with your values:
# - SNOWFLAKE_ACCOUNT=your_account
# - SNOWFLAKE_USER=your_username
# - SNOWFLAKE_PASSWORD=your_password
# - ENABLE_SNOWFLAKE=true
# - ENABLE_CORTEX_LLM=true
```

### 2.3 Start Backend
```bash
python run.py
```

Verify: http://localhost:8000/health
Should return: `{"status":"healthy"}`

Verify Snowflake: http://localhost:8000/api/snowflake/health
Should return: `{"status":"healthy","database":"BUGREWIND"}`

---

## Step 3: Ripgrep API Setup (2 min)

### 3.1 Install & Start
```bash
cd ripgrep-api
npm install
npm run dev
```

Verify: http://localhost:3001/health
Should return: `{"success":true,"status":"healthy"}`

---

## Step 4: Postman Setup (5 min)

### 4.1 Import Collections
1. Open Postman Desktop
2. Click **Import** → Select files from `postman/collections/`:
   - `ripgrep-search-module.json`
   - `get-open-prs-module.json`
   - `get-pr-files-module.json`
   - `snowflake-generate-pr.json` ⭐ **NEW!**
   - `create-github-pr-module.json`
   - `send-slack-notification-module.json`

### 4.2 Create Flow Modules
For **each collection** imported:
1. Right-click collection → **"Create Flow Module"**
2. Name it (e.g., "Ripgrep Search Tool")
3. Click **"Create Snapshot"**
4. Save

You should now have 6 Flow Modules.

### 4.3 Import Environment
1. Click **Environments** (left sidebar)
2. Import `postman/environment.example.json`
3. Rename to "PM Copilot - Demo"
4. Fill in your values:
   - `CLAUDE_API_KEY`: (optional, Cortex used instead)
   - `GITHUB_TOKEN`: Your GitHub PAT
   - `GITHUB_REPO_OWNER`: Your GitHub username
   - `GITHUB_REPO_NAME`: Your repo name
   - `SLACK_WEBHOOK_PM`: Your Slack webhook URL
   - `SNOWFLAKE_API_URL`: `http://localhost:8000`

### 4.4 Test Individual Tools
Test each module works:

**Test Ripgrep:**
```bash
curl -X POST http://localhost:3001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "login", "path": "src/"}'
```

**Test Snowflake Cortex:**
```bash
curl -X POST http://localhost:8000/api/snowflake/generate-pr \
  -H "Content-Type: application/json" \
  -d '{
    "feature_request": "fix mobile login",
    "impacted_files": ["src/pages/Login.tsx"],
    "is_new_feature": false,
    "repo_name": "demo/repo"
  }'
```

---

## Step 5: Create AI Agent Flow (10 min)

### 5.1 Create New Flow
1. Click **Flows** (left sidebar)
2. **Create New Flow** → Name: "PM-Copilot-Hybrid-AI"

### 5.2 Add Blocks
Add these blocks in order:

```
[Start Block]
  ↓
[AI Agent Block]
  ↓
[Output Block]
```

### 5.3 Configure Start Block
- Type: "Request-triggered Action"
- Expected input:
  ```json
  {
    "text": "fix mobile login responsive design"
  }
  ```

### 5.4 Configure AI Agent Block

**Add Tools** (click "Tools" → "Add Tool"):
- ☑️ Ripgrep Search Tool
- ☑️ Get Open PRs Tool
- ☑️ Get PR Files Tool
- ☑️ **Snowflake Generate PR Tool** ⭐
- ☑️ Create GitHub PR Tool
- ☑️ Send Slack Notification Tool

**System Prompt:**

Paste this into the AI Agent prompt field:

```
You are a PM Copilot AI Agent using HYBRID AI architecture.

INPUT: {{Start.text}} - Feature request from PM

HYBRID AI APPROACH:
- YOU (Postman AI Agent / GPT-5) = Orchestration brain (decide WHEN to call tools)
- Snowflake Cortex (Mistral) = Code generation brain (decide WHAT code to write)

YOUR WORKFLOW:

1. PARSE INTENT
   Extract: feature_name, search_keywords from {{Start.text}}

2. SEARCH CODEBASE
   Call **Ripgrep Search Tool** with:
   - query: search_keywords
   - path: "src/"
   Store: impacted_files, is_new_feature, total_files

3. CONFLICT DETECTION (optional for demo)
   Call **Get Open PRs Tool** to check for conflicts
   For each PR: Call **Get PR Files Tool**
   Calculate overlap and conflict scores

4. GENERATE PR CONTENT ⭐ KEY STEP!
   Call **Snowflake Generate PR Tool** with:
   - feature_request: {{Start.text}}
   - impacted_files: from step 2
   - is_new_feature: from step 2
   - repo_name: "{{GITHUB_REPO_OWNER}}/{{GITHUB_REPO_NAME}}"
   - conflict_info: from step 3 (if any)

   This calls Snowflake Cortex LLM to generate:
   - pr_title
   - pr_description
   - branch_name

   AND stores execution data in Snowflake!

5. CREATE GITHUB PR
   Call **Create GitHub PR Tool** with Cortex-generated content

6. NOTIFY TEAM
   Call **Send Slack Notification Tool** with:
   - PR URL
   - "Generated by: Postman AI Agent + Snowflake Cortex"

OUTPUT FORMAT:
{
  "success": true,
  "pr_url": "...",
  "orchestrated_by": "Postman AI Agent (GPT-5)",
  "generated_by": "Snowflake Cortex (Mistral-Large)",
  "reasoning_trace": [
    "Parsed intent",
    "Searched codebase",
    "Called Snowflake Cortex",
    "Created GitHub PR",
    "Notified Slack"
  ]
}
```

### 5.5 Save and Test
1. Click **Save**
2. Click **Run** (test mode)
3. Input:
   ```json
   {
     "text": "fix mobile login responsive design"
   }
   ```
4. Watch the AI Agent call tools in sequence
5. Verify GitHub PR created and Slack notified

---

## Step 6: Deploy as Action (2 min)

1. Click **Deploy** button
2. Enable **"Public URL"**
3. Copy the Action URL (e.g., `https://flows-action.postman.com/abc123`)
4. Save this URL - you'll use it for Slack integration

---

## Step 7: Slack Integration (3 min)

### 7.1 Create Slack App
1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name: "PM Copilot"
4. Choose your workspace

### 7.2 Enable Slash Commands
1. In app settings → **Slash Commands** → **"Create New Command"**
2. Command: `/impact`
3. Request URL: Your Postman Action URL (from Step 6)
4. Description: "Generate PR from PM spec"
5. Save

### 7.3 Install App
1. **Install App** → Install to workspace
2. Authorize permissions
3. Test in Slack: `/impact fix mobile login`

---

## Testing Checklist

Before demo, verify each component:

### Backend Services
- [ ] Backend running: `curl http://localhost:8000/health`
- [ ] Snowflake connected: `curl http://localhost:8000/api/snowflake/health`
- [ ] Ripgrep running: `curl http://localhost:3001/health`

### Postman Flow
- [ ] All 6 Flow Modules created with snapshots
- [ ] AI Agent Flow configured with system prompt
- [ ] Environment variables set correctly
- [ ] Test run succeeds end-to-end

### Integrations
- [ ] GitHub token valid and has `repo` scope
- [ ] Slack webhook working (test with curl)
- [ ] Snowflake queries run successfully

### Demo Data
- [ ] Snowflake has sample PR generation data
- [ ] Demo queries ready in Snowflake console
- [ ] Test PR can be created in GitHub repo

---

## Demo Day Checklist

### 30 Minutes Before:
- [ ] Start backend: `cd backend && python run.py`
- [ ] Start Ripgrep: `cd ripgrep-api && npm run dev`
- [ ] Open Postman Desktop
- [ ] Open Slack workspace
- [ ] Open Snowflake console with queries ready
- [ ] Open GitHub repository
- [ ] Close all distracting apps
- [ ] Test microphone and screen recording

### 5 Minutes Before:
- [ ] Run end-to-end test once
- [ ] Clear browser cache/cookies if needed
- [ ] Position windows for recording
- [ ] Have demo script (`HYBRID_AI_DEMO_SCENARIO.md`) open

### During Demo:
- [ ] Follow 3-minute script exactly
- [ ] Emphasize "Hybrid AI" multiple times
- [ ] Show Snowflake Cortex generating PR LIVE
- [ ] Demonstrate final Slack notification

---

## Troubleshooting

### "Snowflake not connected"
- Check `.env` has correct credentials
- Verify `ENABLE_SNOWFLAKE=true`
- Test: `curl http://localhost:8000/api/snowflake/health`

### "Cortex LLM disabled"
- Check `.env` has `ENABLE_CORTEX_LLM=true`
- Verify Snowflake account has Enterprise edition
- Test Cortex directly in Snowflake console

### "AI Agent not calling tools"
- Verify Flow Modules have snapshots created
- Check tools are registered in AI Agent block
- Review system prompt for explicit "Call **Tool Name**" instructions

### "GitHub PR creation fails"
- Verify GitHub token has `repo` scope
- Check branch name doesn't already exist
- Ensure you have write access to repository

### "Slack webhook fails"
- Test webhook with curl first
- Verify URL is correct in environment
- Check Slack app is installed to workspace

---

## Expected Demo Metrics

| Metric | Target | How to Verify |
|--------|--------|---------------|
| End-to-End Time | < 30s | Stopwatch in recording |
| Cortex Response | 2-3s | Backend terminal logs |
| API Calls | 4-6 | Postman Flow execution log |
| PR Created | Yes | GitHub repository |
| Slack Notified | Yes | Slack channel message |

---

## Demo Files

- **Scenario**: `HYBRID_AI_DEMO_SCENARIO.md` - 3-minute script
- **Snowflake Queries**: `SNOWFLAKE_SHOWCASE.sql` - Demo queries
- **Table Setup**: `snowflake-pr-generations-table.sql` - DB schema
- **Postman Collection**: `postman/collections/snowflake-generate-pr.json`

---

## Support

If you get stuck:
- Check backend logs: `tail -f backend/logs/app.log`
- Check Postman console for errors
- Review Snowflake query history
- Test each component individually

---

## Success Criteria

✅ Backend services running
✅ Snowflake connected and Cortex working
✅ Postman AI Agent flow executing
✅ GitHub PR created
✅ Slack notification sent
✅ All data stored in Snowflake
✅ Can demonstrate Hybrid AI architecture
✅ 3-minute demo polished and recorded

**Ready to win? Let's go! 🚀**
