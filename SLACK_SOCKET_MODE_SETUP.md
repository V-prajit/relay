# Slack Socket Mode Setup - Complete Guide

**No public URL required!** Socket Mode uses WebSockets instead of HTTP webhooks.

**Time Required:** 20 minutes

---

## What You're Building

```
Slack (#new-channel)
  ↓ /impact command (WebSocket)
  ↓
slack-listener app (localhost)
  ↓ HTTP requests
  ↓
ripgrep API (localhost:3001) + backend (localhost:8000)
  ↓
Notification posted back to Slack
```

**Everything runs on localhost - no deployment needed!**

---

## Part 1: Create Slack App with Socket Mode (10 min)

### Step 1.1: Create New App
1. Go to: https://api.slack.com/apps
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Fill in:
   - **App Name:** `PM Copilot`
   - **Pick a workspace:** Select your workspace (with #new-channel)
5. Click **"Create App"**

---

### Step 1.2: Enable Socket Mode
1. In left sidebar → Click **"Socket Mode"**
2. Toggle **"Enable Socket Mode"** to **ON**
3. You'll see a prompt to generate an App-Level Token
4. Click **"Generate Token and Scopes"**
5. Fill in:
   - **Token Name:** `socket-mode-token`
   - **Scope:** Select `connections:write`
6. Click **"Generate"**
7. **COPY THE TOKEN** (starts with `xapp-`)
   - Example: `xapp-1-A123ABC-456DEF-abc123def456...`
   - ⚠️ **Save this immediately!** You won't see it again
8. Click **"Done"**

**Save to your notes:**
```
SLACK_APP_TOKEN=xapp-1-A123...
```

---

### Step 1.3: Add Bot Token Scopes
1. In left sidebar → Click **"OAuth & Permissions"**
2. Scroll to **"Scopes"** → **"Bot Token Scopes"**
3. Click **"Add an OAuth Scope"**
4. Add these scopes:
   - `chat:write` (post messages to channels)
   - `commands` (use slash commands)
   - `users:read` (read user info for mentions)

---

### Step 1.4: Install App to Workspace
1. Scroll up to **"OAuth Tokens for Your Workspace"**
2. Click **"Install to Workspace"** button
3. Review permissions → Click **"Allow"**
4. You'll see **"Bot User OAuth Token"**
5. **COPY THE TOKEN** (starts with `xoxb-`)
   - Example: `xoxb-123456789-987654321-abcdefghijk...`

**Save to your notes:**
```
SLACK_BOT_TOKEN=xoxb-123456789...
```

---

### Step 1.5: Create Slash Command
1. In left sidebar → Click **"Slash Commands"**
2. Click **"Create New Command"**
3. Fill in:
   - **Command:** `/impact`
   - **Request URL:** Leave blank or put `http://localhost` (doesn't matter for Socket Mode!)
   - **Short Description:** `Generate GitHub PR from feature request`
   - **Usage Hint:** `[feature description]`
4. Click **"Save"**

**Important:** For Socket Mode, the Request URL is ignored. Your app listens via WebSocket instead!

---

### Step 1.6: Verify Installation
1. Open **Slack desktop/web app**
2. Go to **#new-channel**
3. Type `/` (forward slash)
4. You should see `/impact` in the command list
5. If you see it → Installation successful! ✅

---

## Part 2: Configure Your Local App (5 min)

### Step 2.1: Create Environment File
```bash
cd slack-listener
cp .env.example .env
```

### Step 2.2: Edit .env File
Open `.env` in your editor and fill in:

```bash
# Slack Tokens (from Part 1)
SLACK_BOT_TOKEN=xoxb-123456789-987654321-abcdefghijk...
SLACK_APP_TOKEN=xapp-1-A123ABC-456DEF-abc123def456...

# Local Services (verify these match your setup)
RIPGREP_API_URL=http://localhost:3001
BACKEND_API_URL=http://localhost:8000

# GitHub (optional - for auto PR creation)
GITHUB_TOKEN=ghp_your_github_token_here
REPO_OWNER=V-prajit
REPO_NAME=youareabsolutelyright

# Set to 'true' to auto-create GitHub PRs, 'false' to skip
AUTO_CREATE_PR=false
```

**Save the file.**

### Step 2.3: Install Dependencies
```bash
cd slack-listener
npm install
```

Expected output:
```
added 150 packages in 10s
```

---

## Part 3: Start All Services (3 min)

You need **3 terminals running**:

### Terminal 1: Backend (Snowflake Cortex)
```bash
cd backend
python run.py
```

**Wait for:**
```
==========================================================
Server running on: http://localhost:8000
==========================================================
```

### Terminal 2: Ripgrep API
```bash
cd ripgrep-api
npm run dev
```

**Wait for:**
```
Server running on port 3001
```

### Terminal 3: Slack Listener (Socket Mode)
```bash
cd slack-listener
npm start
```

**Wait for:**
```
==========================================================
⚡️ PM Copilot Slack Listener (Socket Mode)
==========================================================
Status: RUNNING ✅
Listening for /impact commands in Slack...
```

**All 3 services must be running!**

---

## Part 4: Test the Workflow (5 min)

### Test 1: Simple Command

1. Go to **#new-channel** in Slack
2. Type:
   ```
   /impact test feature request
   ```
3. Press **Enter**

**Expected:**
- Slack shows: "⏳ Processing your request: test feature request"
- Check **Terminal 3** (slack-listener) for logs:
  ```
  📨 Received /impact command from @yourname
  🔍 Step 1: Searching codebase...
  🤖 Step 2: Generating PR...
  💬 Step 3: Sending notification...
  ✅ WORKFLOW COMPLETE!
  ```
- After ~30 seconds, **notification appears in #new-channel** with:
  - ✅ Task Created
  - Files Impacted
  - Branch name
  - View Repo button

### Test 2: Real Feature Request

1. **Customer** (you or teammate) posts:
   ```
   The mobile login page is completely broken! 😡
   ```

2. **PM** (you) responds:
   ```
   /impact fix mobile login responsive design
   ```

3. **Watch the magic:**
   - Immediate response in Slack
   - Logs in Terminal 3 showing each step
   - Rich notification with:
     - Feature request
     - Impacted files (e.g., `Login.tsx`, `mobile.css`)
     - Generated branch name
     - PR description preview

**Success!** ✅

---

## Troubleshooting

### "Command not recognized"
**Symptoms:** Type `/` in Slack, don't see `/impact`

**Solutions:**
1. Check app is installed: Slack settings → Apps → "PM Copilot"
2. Reinstall app:
   - api.slack.com/apps → Your App → OAuth & Permissions
   - Click "Reinstall to Workspace"
3. Verify command exists: Slash Commands section

---

### "Socket mode connection failed"
**Symptoms:** slack-listener logs show connection errors

**Solutions:**
1. Verify `SLACK_APP_TOKEN` starts with `xapp-`
2. Check Socket Mode is enabled:
   - api.slack.com/apps → Your App → Socket Mode
   - Should be toggled ON
3. Regenerate App Token if needed:
   - Basic Information → App-Level Tokens
   - Delete old token, create new one with `connections:write` scope

---

### "Missing scope" error
**Symptoms:** Error about missing permissions

**Solutions:**
1. Go to: OAuth & Permissions → Bot Token Scopes
2. Add missing scopes:
   - `chat:write`
   - `commands`
   - `users:read`
3. Reinstall app to workspace

---

### "Service unavailable" or timeout
**Symptoms:** Command times out, no notification

**Solutions:**
1. Check all services running:
   ```bash
   curl http://localhost:8000/health  # Backend
   curl http://localhost:3001/api/health  # Ripgrep
   ```
2. Check Terminal 3 logs for error details
3. Verify `.env` URLs match running services:
   - `RIPGREP_API_URL=http://localhost:3001`
   - `BACKEND_API_URL=http://localhost:8000`

---

### "GitHub PR creation failed"
**Symptoms:** Logs show GitHub error, but notification still appears

**Solutions:**
- **This is optional!** The workflow continues without it
- Set `AUTO_CREATE_PR=false` in `.env` to skip
- If you want GitHub PRs:
  - Check `GITHUB_TOKEN` has `repo` scope
  - Verify `REPO_OWNER` and `REPO_NAME` are correct
  - Make sure branch doesn't already exist

---

## Demo Workflow

### Pre-Demo Checklist
- [ ] All 3 services running (backend, ripgrep, slack-listener)
- [ ] Tested `/impact` command at least once successfully
- [ ] #new-channel clean and ready
- [ ] Slack open on screen
- [ ] Optional: Screen recording software ready

### Demo Script (60 seconds)

**0:00 - Customer Complaint**
Type in #new-channel:
```
The mobile login is completely broken! Users can't sign in 😡
```

**0:10 - PM Response**
Type in same channel:
```
/impact fix mobile login responsive design
```

**0:15 - Show Terminals (optional)**
Switch to Terminal 3 to show logs:
- "Received /impact command..."
- "Step 1: Searching codebase..."
- "Step 2: Generating PR..."

**0:30 - Notification Appears**
Switch back to Slack - notification appears with:
- ✅ Task Created
- Files found
- Branch name
- PR description preview

**0:45 - Explain**
"30 seconds from complaint to actionable task. No meetings, no confusion."

---

## Advantages of Socket Mode

✅ **No public URL required** - Perfect for localhost development
✅ **No ngrok/tunnel needed** - Saves setup time
✅ **More reliable** - Direct WebSocket connection
✅ **Faster** - No cloud round-trip for your services
✅ **Free** - No paid hosting/tunnel services
✅ **Secure** - Services stay on your machine

---

## Environment Variables Reference

| Variable | Where to Get It | Required |
|----------|----------------|----------|
| `SLACK_BOT_TOKEN` | OAuth & Permissions → Bot User OAuth Token | ✅ Yes |
| `SLACK_APP_TOKEN` | Basic Information → App-Level Tokens | ✅ Yes |
| `RIPGREP_API_URL` | Your local setup (default: `http://localhost:3001`) | ✅ Yes |
| `BACKEND_API_URL` | Your local setup (default: `http://localhost:8000`) | ✅ Yes |
| `GITHUB_TOKEN` | github.com/settings/tokens | ⭐ Optional |
| `REPO_OWNER` | Your GitHub username | ⭐ Optional |
| `REPO_NAME` | Your repo name | ⭐ Optional |
| `AUTO_CREATE_PR` | `true` or `false` | ⭐ Optional |

---

## What Happens When You Run `/impact`

1. **Slack sends WebSocket message** to your app
2. **App acknowledges** immediately ("⏳ Processing...")
3. **App calls Ripgrep API** (localhost:3001) to search code
4. **App calls Snowflake Cortex** (localhost:8000) to generate PR
5. **App optionally creates GitHub PR** (if configured)
6. **App posts rich notification** back to Slack channel
7. **Total time:** ~30 seconds

---

## Logs Example

```
==========================================================
📨 Received /impact command from @alice
Feature request: "fix mobile login responsive design"
==========================================================

🔍 Step 1: Searching codebase with Ripgrep...
   ✅ Found 2 file(s)
   📁 Files: src/pages/Login.tsx, src/styles/mobile.css
   🆕 New feature: false

🤖 Step 2: Generating PR with Snowflake Cortex...
   ✅ Generated PR: "fix: Mobile login responsive design for iPhone 15"
   🌿 Branch: fix/mobile-login-responsive-20250126-abc123

📝 Step 3: Skipping GitHub PR creation (set AUTO_CREATE_PR=true to enable)

💬 Step 4: Sending notification to Slack...
   ✅ Notification sent to Slack!

==========================================================
✅ WORKFLOW COMPLETE!
==========================================================
```

---

## Next Steps

### After Setup Works:
1. ✅ Practice demo 3-5 times
2. ✅ Test with different feature requests
3. ✅ Optionally enable `AUTO_CREATE_PR=true`
4. ✅ Prepare backup screenshots (in case live demo fails)
5. ✅ Have teammate work on Agentverse deployment (bonus points)

### Optional Enhancements:
- Add more Slack Block Kit formatting
- Implement GitHub branch creation before PR
- Add conflict detection in notification
- Store execution history locally

---

## Support Resources

- **App Code:** `slack-listener/index.js`
- **Demo Script:** `DEMO_SCRIPT_SLACK.md` (adapt for Socket Mode)
- **Slack Socket Mode Docs:** https://api.slack.com/apis/socket-mode
- **Slack Bolt SDK:** https://slack.dev/bolt-js/concepts#socket-mode
- **Project README:** `slack-listener/README.md`

---

**Setup Complete!** 🎉

You now have a fully functional PM Copilot running entirely on localhost with no public URLs!

**Total time:** ~20 minutes
**Services needed:** 3 (backend, ripgrep, slack-listener)
**Demo time:** 60 seconds
**Impressiveness:** ⭐⭐⭐⭐⭐

---

_Last updated: 2025-01-26_
_Socket Mode: No public URL required!_
