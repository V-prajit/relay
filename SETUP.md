# Complete Setup Guide

This guide walks you through setting up the PM Copilot from scratch. Total time: ~45 minutes.

---

## Prerequisites

Before starting, ensure you have:

- [x] **Postman Desktop** (v11.42.3+) - https://www.postman.com/downloads/
- [x] **Node.js** (18+) - https://nodejs.org/
- [x] **GitHub Account** - https://github.com/
- [x] **Slack Workspace** (admin access) - https://slack.com/
- [x] **Claude API Key** - https://console.anthropic.com/
- [x] **Text Editor** (VS Code recommended)

---

## Part 1: Ripgrep API Setup (10 min)

### Step 1.1: Install Dependencies

```bash
cd ripgrep-api
npm install
```

### Step 1.2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
PORT=3001
ALLOWED_ORIGINS=*
MAX_SEARCH_RESULTS=50
DEFAULT_SEARCH_PATH=./
```

### Step 1.3: Start Server

```bash
npm run dev
```

Expected output:
```
Server running on port 3001
Ripgrep API ready
```

### Step 1.4: Test

```bash
curl http://localhost:3001/api/health
```

Expected response:
```json
{"status":"ok","timestamp":"2025-01-26T..."}
```

**Test search**:
```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"import","path":"src/","type":"tsx"}'
```

Should return files matching the query.

---

## Part 2: Postman Flows Setup (20 min)

### Step 2.1: Import Flow Modules

1. **Open Postman Desktop** (v11.42.3+)
2. Click **Collections** (left sidebar)
3. Click **Import** button
4. Navigate to `postman/modules/` folder
5. Select all 6 JSON files:
   - `ripgrep-search-module.json`
   - `get-open-prs-module.json`
   - `get-pr-files-module.json`
   - `claude-generate-pr-module.json`
   - `create-github-pr-module.json`
   - `send-slack-notification-module.json`
6. Click **Import**

### Step 2.2: Create Flow Modules

For **each of the 6 collections**:

1. Find collection in sidebar
2. Right-click collection name
3. Select **"Create Flow Module"**
4. Give it a descriptive name:
   - "Ripgrep Search Tool"
   - "Get Open PRs Tool"
   - "Get PR Files Tool"
   - "Claude Generate PR Tool"
   - "Create GitHub PR Tool"
   - "Send Slack Notification Tool"
5. Click **Create**

✅ You should now have 6 flow modules available

### Step 2.3: Create Environment

1. Click **Environments** (left sidebar)
2. Click **Create Environment**
3. Name it: `pm-copilot-dev`
4. Add these variables:

| Variable | Initial Value | Type |
|----------|--------------|------|
| `RIPGREP_API_URL` | `http://localhost:3001` | default |
| `CLAUDE_API_KEY` | `sk-ant-...` (your key) | secret |
| `GITHUB_TOKEN` | `ghp_...` (create below) | secret |
| `SLACK_WEBHOOK_PM` | (create later) | secret |
| `REPO_OWNER` | `your-github-username` | default |
| `REPO_NAME` | `youareabsolutelyright` | default |

5. Click **Save**
6. Select this environment (dropdown at top right)

**Creating GitHub Token**:
1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Name: "PM Copilot"
4. Select scopes: ✅ `repo` (all sub-scopes)
5. Click **Generate token**
6. **Copy token** (save it!)
7. Paste into Postman environment

### Step 2.4: Create Main Flow

1. Click **Flows** (left sidebar)
2. Click **Create Flow**
3. Name: `PM-Copilot-Main`
4. **Add Start Block**:
   - Drag **Start** block to canvas
   - Click block → Select **"Request-triggered Action"**
   - This allows external HTTP calls (for Slack)

5. **Add AI Agent Block**:
   - Drag **AI Agent** block next to Start
   - Connect Start → AI Agent (drag from right dot)

6. **Add Output Block**:
   - Drag **Output** block next to AI Agent
   - Connect AI Agent → Output

### Step 2.5: Configure AI Agent

1. Click **AI Agent** block
2. In right panel, click **Tools** section
3. Click **Add Tool**
4. Select all 6 flow modules you created
5. Click **Add**

6. Click **Prompt** section
7. Copy entire prompt from `postman/AI-AGENT-CONFIGURATION.md`
8. Paste into prompt field
9. Click **Save**

### Step 2.6: Test Flow

1. Click **Run** (top right)
2. Input test data:
   ```json
   {
     "text": "Add dark mode toggle to settings",
     "user_id": "@alice"
   }
   ```
3. Click **Run**
4. Watch execution (this may take 30-60 seconds)

Expected behavior:
- AI Agent calls Ripgrep Search Tool
- AI Agent calls Get Open PRs Tool
- AI Agent calls Claude Generate PR Tool
- (May fail on GitHub PR creation if no branch exists - that's OK for now)

**Check execution history**:
- Click **Console** (bottom)
- See tool calls made by AI Agent
- Verify Ripgrep returned files
- Verify Claude generated PR content

✅ If you see tool calls in console, AI Agent is working!

### Step 2.7: Deploy as Action

1. Click **Deploy** (top right in flow)
2. Select **"Enable Public URL"**
3. Click **Create**
4. **Copy the Action URL** (e.g., `https://flows-action.postman.com/abc123...`)
5. Save this URL somewhere safe (you'll need it for Slack)

---

## Part 3: Slack Integration (10 min)

### Step 3.1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click **Create New App**
3. Select **"From scratch"**
4. Fill in:
   - **App Name**: `PM Copilot`
   - **Pick a workspace**: Select your workspace
5. Click **Create App**

### Step 3.2: Enable Slash Command

1. In left sidebar, click **Slash Commands**
2. Click **Create New Command**
3. Fill in:
   - **Command**: `/impact`
   - **Request URL**: Your Postman Action URL (from Step 2.7)
   - **Short Description**: `Generate PR from feature request`
   - **Usage Hint**: `[feature description]`
4. Click **Save**

### Step 3.3: Enable Incoming Webhooks

1. In left sidebar, click **Incoming Webhooks**
2. Toggle switch at top to **ON**
3. Scroll to **"Webhook URLs for Your Workspace"**
4. Click **Add New Webhook to Workspace**
5. Select a channel (e.g., `#new-channel`)
6. Click **Allow**
7. **Copy the webhook URL** (looks like `https://hooks.slack.com/services/...`)

### Step 3.4: Update Postman Environment

1. Go back to Postman Desktop
2. Open Environments (left sidebar)
3. Select `pm-copilot-dev` environment
4. Find `SLACK_WEBHOOK_PM` variable
5. Paste webhook URL as value
6. Change type to **secret**
7. Click **Save**

### Step 3.5: Install Slack App

1. Back in Slack API page (api.slack.com/apps)
2. In left sidebar, click **Install App**
3. Click **Install to Workspace**
4. Review permissions
5. Click **Allow**

✅ You should see: "Successfully installed to [Your Workspace]"

### Step 3.6: Test in Slack

1. Open **Slack desktop/web app**
2. Go to the channel where you installed the webhook
3. Type: `/impact "test feature request"`
4. Press **Enter**

Expected:
- (Immediate) Slack shows loading or acknowledgment
- (30-60 seconds later) Notification appears in channel with PR details

**If it doesn't work**, see Troubleshooting section below.

---

## Part 4: Dashboard Setup (Optional, 5 min)

### Step 4.1: Dashboard API

```bash
cd dashboard-api
npm install
cp .env.example .env
npm run dev
```

Runs on: http://localhost:3002

### Step 4.2: Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:3002
```

Start:
```bash
npm run dev
```

Runs on: http://localhost:3000

Visit: http://localhost:3000/dashboard

---

## Part 5: End-to-End Test (5 min)

### Scenario: New Feature Request

1. **In Slack**, type:
   ```
   /impact "Add OAuth login support"
   ```

2. **Expected flow**:
   - Postman AI Agent receives request
   - Ripgrep searches for "OAuth" → finds 0 files
   - Marks as `is_new_feature: true`
   - Checks open PRs (none related)
   - Claude generates new file structure
   - Creates GitHub PR (or returns content)
   - Slack notification with details

3. **Check Slack notification**:
   - Should show feature name
   - List impacted files
   - Reasoning trace (7+ steps)
   - [View PR] button (if PR created)

### Scenario: Existing Feature with Conflict

1. **Setup**: Create a PR that modifies `Settings.tsx` (leave it open)

2. **In Slack**, type:
   ```
   /impact "Update Settings page with dark mode toggle"
   ```

3. **Expected flow**:
   - Ripgrep finds `Settings.tsx`, `theme.ts`
   - Checks open PRs → finds your test PR
   - Detects overlap: `Settings.tsx` in both
   - Conflict score = 50%
   - Creates PR with warning
   - Slack notification: ⚠️ Conflict Detected

4. **Check Slack notification**:
   - Should show conflict warning
   - List overlapping files
   - Link to conflicting PR
   - Suggest coordination

---

## Troubleshooting

### Ripgrep API Issues

**Error**: "EADDRINUSE: port 3001 already in use"

**Solution**:
```bash
lsof -ti:3001 | xargs kill -9
cd ripgrep-api && npm run dev
```

**Error**: "404 Not Found" when calling `/api/search`

**Solution**:
- Check URL: Must be `http://localhost:3001/api/search` (with `/api`)
- Verify server is running: `curl http://localhost:3001/api/health`

---

### Postman Flow Issues

**Error**: "Tool not found"

**Solution**:
- Ensure you created Flow Modules (right-click collection → "Create Flow Module")
- Modules must have snapshots to be usable as tools

**Error**: "Variable not found: {{Start.text}}"

**Solution**:
- Check Start block is connected to AI Agent
- Verify Start block type is "Request-triggered Action"

**Error**: "422 Unprocessable Entity" from APIs

**Solution**:
- Add `Content-Type: application/json` header to all HTTP blocks
- Check request body format matches expected schema
- See `docs/POSTMAN_FLOW_FIX_GUIDE.md` for detailed fixes

**Error**: AI Agent not calling tools

**Solution**:
- Tools must be registered in AI Agent settings
- Prompt must explicitly reference tool names
- Use exact module names like "Ripgrep Search Tool"

---

### GitHub Issues

**Error**: "401 Unauthorized" when creating PR

**Solution**:
- Check GitHub token is valid: `curl https://api.github.com/user -H "Authorization: Bearer {token}"`
- Token must have `repo` scope
- Generate new token if needed

**Error**: "404 Not Found" when creating PR

**Solution**:
- Verify `REPO_OWNER` and `REPO_NAME` are correct
- Check repository exists and you have access
- Repository must be accessible with your token

---

### Slack Issues

**Error**: "/impact command not showing"

**Solution**:
- Reinstall Slack app (api.slack.com/apps → Your App → Reinstall)
- Verify command appears when typing `/` in Slack
- Check app is installed to correct workspace

**Error**: "dispatch_failed" error

**Solution**:
- Verify Postman Action URL is correct in Slash Command settings
- Test Action URL with curl:
  ```bash
  curl -X POST {your-action-url} \
    -H "Content-Type: application/json" \
    -d '{"text":"test"}'
  ```

**Error**: "timeout" after 3 seconds

**Solution** (Optional - for advanced users):
- Add immediate response in Postman Flow:
  - After Start block, add Send block
  - Response: `{"text":"Processing your request..."}`
  - This acknowledges Slack immediately while workflow runs

**Error**: No notification appears

**Solution**:
- Test webhook directly:
  ```bash
  curl -X POST {your-webhook-url} \
    -H "Content-Type: application/json" \
    -d '{"text":"test message"}'
  ```
- Check webhook is for correct channel
- Verify `SLACK_WEBHOOK_PM` variable is set in Postman environment

---

### Quick Health Checks

```bash
# Check all services
curl http://localhost:3001/api/health  # Ripgrep API
curl http://localhost:3002/api/health  # Dashboard API

# Check what's running
lsof -i :3001,3002,3000

# Restart everything
lsof -ti:3001,3002,3000 | xargs kill -9
cd ripgrep-api && npm run dev &
cd dashboard-api && npm run dev &
cd frontend && npm run dev &
```

---

## Next Steps

### For Development

1. **Read** `CLAUDE.md` for developer guidelines
2. **Customize** AI Agent prompt for your needs
3. **Add** new Flow Modules for additional APIs
4. **Deploy** dashboard to production (Vercel, Railway, etc.)

### For Demo/Presentation

1. **Practice** the Slack workflow
2. **Record** a demo video (3 minutes)
3. **Prepare** judge-clickable proof:
   - Live Postman Action URL
   - Live Slack workspace invite
   - GitHub repo with generated PRs
4. **Document** in README and CLAUDE.md

### For Production

1. **Add authentication** to dashboard
2. **Use database** instead of JSON file storage
3. **Implement** proper error handling and logging
4. **Set up** CI/CD pipeline (see `docs/CI_CD_SETUP.md`)
5. **Monitor** with observability tools

---

## Useful Commands

### Ripgrep API

```bash
# Start
cd ripgrep-api && npm run dev

# Test search
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"ProfileCard"}'
```

### Dashboard

```bash
# Start API
cd dashboard-api && npm run dev

# Start Frontend
cd frontend && npm run dev
```

### Debugging

```bash
# Check ports
lsof -i :3001,3002,3000

# Kill all
lsof -ti:3001,3002,3000 | xargs kill -9

# View logs (if using PM2 or similar)
tail -f logs/*.log
```

---

## Configuration Reference

### Ripgrep API (.env)

```env
PORT=3001
ALLOWED_ORIGINS=*
MAX_SEARCH_RESULTS=50
DEFAULT_SEARCH_PATH=./
```

### Postman Environment Variables

```
RIPGREP_API_URL = http://localhost:3001
CLAUDE_API_KEY = sk-ant-... (secret)
GITHUB_TOKEN = ghp_... (secret)
SLACK_WEBHOOK_PM = https://hooks.slack.com/services/... (secret)
REPO_OWNER = your-username
REPO_NAME = your-repo
```

### Dashboard (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:3002
```

---

## Security Notes

### DO NOT commit these to git:
- `.env` files
- API keys
- GitHub tokens
- Slack webhook URLs

### Best Practices:
- Mark sensitive variables as "secret" in Postman
- Use different tokens for dev/prod
- Rotate keys regularly
- Keep `.env` files in `.gitignore`

---

## Resources

**Project Documentation**:
- `README.md` - Project overview
- `CLAUDE.md` - Developer instructions
- `postman/AI-AGENT-CONFIGURATION.md` - AI Agent prompt
- `docs/POSTMAN_FLOW_NEW_FEATURES.md` - Handling new features
- `docs/POSTMAN_FLOW_FIX_GUIDE.md` - Common fixes

**External Documentation**:
- [Postman Flows](https://learning.postman.com/docs/postman-flows/)
- [AI Agent Block](https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/)
- [Claude API](https://docs.claude.com/en/api/messages)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Slack Block Kit](https://docs.slack.dev/block-kit/)

---

## Support

**Issues**:
- Check troubleshooting section above
- See `CLAUDE.md` for detailed debugging
- Open GitHub issue if problem persists

**Community**:
- Postman Community: https://community.postman.com/
- Slack API Community: https://api.slack.com/community

---

**Setup Complete! 🎉**

You should now have a working PM Copilot that can generate PRs from Slack commands.

*From vague PM spec to production-ready PR in 30 seconds.*
