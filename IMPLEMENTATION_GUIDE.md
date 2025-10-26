# PM Copilot - Complete Implementation Guide

This guide walks you through implementing **DEV 1: The Architect** features - AI Agent-driven conflict detection with a live visualizer dashboard.

---

## What You're Building

✅ **6 Reusable Flow Modules** (tools for AI Agent)
✅ **AI Agent Configuration** (autonomous conflict detection)
✅ **Enhanced Slack Notifications** (with reasoning traces)
✅ **Dashboard API** (Express.js backend for analytics)
✅ **Visualizer Dashboard** (Next.js frontend)

**Total Implementation Time**: 6-7 hours

---

## Part 1: Postman Flow Modules (2 hours)

### Step 1: Import Flow Module Collections

1. **Open Postman Desktop**
2. Go to **Collections** → **Import**
3. Import all 6 module JSON files from `postman/modules/`:
   - `ripgrep-search-module.json`
   - `get-open-prs-module.json`
   - `get-pr-files-module.json`
   - `claude-generate-pr-module.json`
   - `create-github-pr-module.json`
   - `send-slack-notification-module.json`

### Step 2: Create Flow Modules

For **each collection**:

1. Right-click collection → **"Create Flow Module"**
2. This creates a snapshot of the HTTP request
3. Give it a descriptive name (e.g., "Ripgrep Search Tool")
4. Save the module

**Why?** Flow modules are reusable tools that the AI Agent can call autonomously.

### Step 3: Test Each Module Individually

Before using in AI Agent, test each module:

1. **Ripgrep Search**:
   - Set variable `query` = "ProfileCard"
   - Run → Should find files
2. **Get Open PRs**:
   - Ensure `GITHUB_TOKEN` is set
   - Run → Should list open PRs
3. **Get PR Files**:
   - Set `pr_number` = (an existing PR)
   - Run → Should list changed files

Test all 6 modules to ensure they work standalone.

---

## Part 2: AI Agent Configuration (1 hour)

### Step 1: Create Main Flow

1. **Flows** → **Create New Flow** → Name it "PM-Copilot-v2"
2. Add **Start Block**:
   - Type: "Request-triggered Action"
   - Input schema: `{"text": string, "user_id": string}`
3. Add **AI Agent Block**
4. Add **Output Block**

Connect: `Start → AI Agent → Output`

### Step 2: Register Tools in AI Agent

1. Click the **AI Agent Block**
2. Go to **Tools** section
3. Click **"Add Tool"**
4. Select all 6 flow modules you created
5. Save

The AI Agent can now call these modules autonomously!

### Step 3: Configure AI Agent Prompt

Copy the system prompt from `postman/AI-AGENT-CONFIGURATION.md` (starting at "You are a PM Copilot AI...").

Paste it into the AI Agent's **Prompt** field.

This prompt tells the AI Agent:
- How to parse user requests
- When to call each tool
- How to detect conflicts
- How to format output

### Step 4: Test the Flow

1. **Save** the flow
2. Click **"Run"** (test mode)
3. Input test data:
   ```json
   {
     "text": "Add ProfileCard to /users",
     "user_id": "@alice"
   }
   ```
4. **Watch the AI Agent work!**
   - It will automatically call Ripgrep Search
   - Then Get Open PRs
   - Then Get PR Files (for each open PR)
   - Calculate conflict scores
   - Call Claude to generate PR
   - Create GitHub PR
   - Send Slack notification

Check the **Flow Execution History** to see the reasoning trace.

---

## Part 3: Deploy as Postman Action (15 min)

1. In your flow, click **"Deploy"**
2. Select **"Public URL"**
3. Copy the Action URL (e.g., `https://flows-action.postman.com/abc123`)
4. Save

Now your flow is accessible via HTTP!

### Configure Slack Slash Command

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click your app → **Slash Commands**
3. Create new command:
   - Command: `/impact`
   - Request URL: Your Postman Action URL
   - Description: "Generate PR from PM spec"
4. **Install** app to your workspace

**Test**: In Slack, type `/impact "Add dark mode toggle"`

---

## Part 4: Dashboard API Backend (1 hour)

### Step 1: Install Dependencies

```bash
cd dashboard-api
npm install
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit if needed (defaults work fine)
```

### Step 3: Start the Server

```bash
npm run dev
```

Server runs on **http://localhost:3002**

### Step 4: Connect Postman Flow to Dashboard

In your Postman Flow, add one more block:

1. Add **HTTP Request** block after AI Agent
2. Configure:
   - Method: POST
   - URL: `http://localhost:3002/api/webhook/flow-complete`
   - Body: Pass the AI Agent's output directly
3. Connect: `AI Agent → HTTP (Dashboard API) → Output`

Now every flow execution will be stored in the dashboard!

---

## Part 5: Dashboard Frontend (2 hours)

### Step 1: Configure Frontend

```bash
cd frontend
```

Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:3002
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Start Dashboard

```bash
npm run dev
```

Dashboard runs on **http://localhost:3000**

### Step 4: View Dashboard

Open browser: **http://localhost:3000/dashboard**

You should see:
- ✅ Stats overview (total executions, conflicts, etc.)
- ✅ Risk meter showing average conflict score
- ✅ Recent executions timeline
- ✅ Top features

Click on any execution → See detailed reasoning trace!

---

## Part 6: Testing End-to-End (30 min)

### Test Scenario 1: New Feature (No Conflicts)

1. In Slack: `/impact "Add OAuth login support"`
2. **Expected Flow**:
   - AI Agent parses: feature_name = "oauth-login"
   - Ripgrep searches for "oauth" → finds 0 files
   - Marks as `is_new_feature: true`
   - Checks open PRs → no OAuth-related PRs
   - Conflict score = 0%
   - Claude generates new file structure
   - Creates GitHub PR
   - Slack notification: ✅ PR Created (No Conflicts)
   - Dashboard shows execution with green status

### Test Scenario 2: Existing Feature with Conflict

1. **Setup**: Create a PR that modifies `Settings.tsx` (leave it open)
2. In Slack: `/impact "Update Settings page with dark mode toggle"`
3. **Expected Flow**:
   - AI Agent searches for "Settings dark mode"
   - Finds `Settings.tsx`, `theme.ts`
   - Checks open PRs → finds your open PR
   - Detects overlap: `Settings.tsx` in both
   - Conflict score = 50% (1 of 2 files)
   - Creates PR with conflict warning
   - Slack notification: ⚠️ Conflict Detected (50% risk)
   - Dashboard shows yellow warning badge

---

## Troubleshooting

### "Tool not found" Error

**Cause**: Flow module doesn't have a snapshot

**Fix**:
1. Open the collection
2. Right-click → "Create Flow Module"
3. Save with a clear name

### AI Agent Not Calling Tools

**Cause**: Prompt doesn't explicitly mention tool names

**Fix**: Use exact tool names in prompt:
- ❌ "Search the codebase"
- ✅ "Call the **Ripgrep Search Module** with query..."

### Conflict Detection Always Shows 0%

**Cause**: GitHub API not returning PR files

**Fix**:
1. Check `GITHUB_TOKEN` has `repo` scope
2. Test "Get PR Files" module manually
3. Verify PR numbers are correct

### Dashboard Shows No Data

**Cause**: Flow not sending data to webhook

**Fix**:
1. Check Dashboard API is running (`npm run dev`)
2. Verify HTTP block URL: `http://localhost:3002/api/webhook/flow-complete`
3. Check Dashboard API logs for incoming requests

### Slack Notifications Not Sending

**Cause**: Invalid webhook URL

**Fix**:
1. Go to Slack App → Incoming Webhooks
2. Copy webhook URL
3. Update `SLACK_WEBHOOK_PM` in Postman environment
4. Test manually: `curl -X POST <webhook_url> -d '{"text":"test"}'`

---

## Advanced Customization

### Adjust Conflict Risk Thresholds

Edit AI Agent prompt to change when warnings are shown:

```
If conflict_score > 70%:  # Changed from 50%
  - Add strong warning
```

### Add More Tools

Create new flow modules for:
- **Calendar API**: Check engineer availability
- **Jira API**: Create tasks automatically
- **CodeRabbit**: Attach AI code review

Then register them as tools in the AI Agent!

### Customize Slack Notifications

Edit `send-slack-notification-module.json`:
- Change colors, emojis
- Add more fields
- Include screenshots

### Switch to Database

Replace JSON file storage in Dashboard API:

```bash
npm install pg  # or mongodb
```

Update routes to use database instead of `fs.readFile/writeFile`.

---

## Deployment (Production)

### Deploy Dashboard API

**DigitalOcean App Platform**:
1. Connect GitHub repo
2. Set:
   - Build: `npm install`
   - Run: `npm start`
   - Port: 3002
3. Deploy

**Railway / Render / Fly.io**: Similar process

### Deploy Frontend

**Vercel** (easiest for Next.js):
```bash
cd frontend
npx vercel
```

Set environment variable:
```
NEXT_PUBLIC_API_URL=https://your-api-url.com
```

### Update Postman Flow

Change webhook URL from `localhost:3002` to your deployed API URL.

---

## Demo for Judges

### What to Show

1. **Slack Command**: `/impact "Add dark mode toggle"`
2. **Wait 5 seconds**
3. **Show Slack Response**:
   - ✅ PR Created
   - 🧠 Reasoning Trace (5+ steps)
   - Files Impacted (2-3 files)
   - Conflict warning (if detected)
   - [View PR] button
4. **Click View PR** → Opens GitHub
5. **Show Dashboard**: http://your-dashboard.com/dashboard
   - Stats overview
   - Risk meter
   - Reasoning trace visualization
6. **Postman Flows Analytics**:
   - Show tool calls made by AI Agent
   - System prompt used

### Judge-Clickable Proof

- ✅ Live Postman Action URL (they can test `/impact` in Slack)
- ✅ Live Dashboard URL (they can browse executions)
- ✅ GitHub repo with open PRs showing conflict detection

---

## Summary

You've built:

✅ **AI Agent-Driven Flow** (not manual loops/decisions)
✅ **Smart Conflict Detection** (compares files with open PRs)
✅ **Reasoning Transparency** (shows every AI decision)
✅ **Live Dashboard** (visualizes conflicts and traces)
✅ **Production-Ready** (can be deployed in <1 hour)

**Total Complexity**: 3 flow blocks + 6 modules
**Total Manual Code**: ~0 (all logic in AI prompt)
**Judge Impressiveness**: 10/10 ⭐

---

## Next Steps

1. ✅ Add Calendar + Slack Bot for availability routing
2. ✅ Integrate Agentverse/ASI:One (Chat Protocol)
3. ✅ Add full D3.js force graph visualization
4. ✅ Deploy to cloud (DigitalOcean, Vercel)
5. ✅ Record 3-min demo video

**You're ready for the hackathon! 🚀**
