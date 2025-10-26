# Slack Integration Setup Guide

**Goal:** Connect your Postman Flow to Slack so PMs can trigger it with `/impact` command.

**Time Required:** 15 minutes

---

## Prerequisites

✅ Postman Flow created and working
✅ Backend services running (Snowflake backend on :8000, Ripgrep on :3001)
✅ Slack workspace where you have admin permissions
✅ Access to #new-channel (or create it)

---

## Part 1: Deploy Postman Flow as Action

### Step 1.1: Open Your Flow in Postman
1. Launch **Postman Desktop** app
2. Go to **Flows** section (left sidebar)
3. Open your main PM Copilot flow
   - Should have blocks: Start → Ripgrep → Snowflake → GitHub → Slack Notification

### Step 1.2: Deploy as Action
1. Click **"Deploy"** button (top right corner)
2. You'll see deployment options:
   - **Option A:** "Enable Public URL"
   - **Option B:** "Create Action"
3. Select either option (both work)
4. Postman will generate a public URL like:
   ```
   https://flows-action.postman.com/abc123def456
   ```
5. **COPY THIS URL** - you'll need it multiple times

### Step 1.3: Save to Environment
1. In Postman, go to **Environments** (left sidebar)
2. Select your active environment (e.g., "dev" or "pm-copilot-env")
3. Add new variable:
   - **Variable:** `ACTION_PUBLIC_URL`
   - **Initial Value:** `https://flows-action.postman.com/abc123def456`
   - **Current Value:** (same)
   - **Type:** default
4. Click **Save**

---

## Part 2: Create & Configure Slack App

### Step 2.1: Create New Slack App
1. Open browser → Go to: https://api.slack.com/apps
2. Click green **"Create New App"** button
3. Select **"From scratch"**
4. Fill in form:
   - **App Name:** `PM Copilot` (or `youareabsolutelyright`)
   - **Pick a workspace to develop your app in:** Select your workspace
5. Click **"Create App"**

You should now see the app configuration page.

---

### Step 2.2: Configure Slash Command

1. In left sidebar, find and click **"Slash Commands"**
2. Click **"Create New Command"** button
3. Fill in the form:

   **Command:**
   ```
   /impact
   ```

   **Request URL:**
   ```
   https://flows-action.postman.com/{your-id-from-part-1}
   ```
   ⚠️ **Important:** Use YOUR Action URL from Part 1, Step 1.2

   **Short Description:**
   ```
   Generate GitHub PR from feature request
   ```

   **Usage Hint:**
   ```
   [feature description]
   ```

   **Escape channels, users, and links sent to your app:**
   - Leave **unchecked**

4. Click **"Save"** at bottom right

You should see your `/impact` command listed now.

---

### Step 2.3: Enable Incoming Webhooks

1. In left sidebar, find and click **"Incoming Webhooks"**
2. Toggle the switch at top to **ON**
3. Scroll down to **"Webhook URLs for Your Workspace"** section
4. Click **"Add New Webhook to Workspace"** button
5. You'll see a channel selector:
   - Search for and select **#new-channel**
   - (If channel doesn't exist, create it first in Slack)
6. Click **"Allow"**
7. You'll return to the Incoming Webhooks page
8. Find your new webhook URL (looks like):
   ```
   https://hooks.slack.com/services/T01ABC123/B01DEF456/xxxxxxxxxxxxxxxxxxx
   ```
9. Click **"Copy"** button next to it
10. **SAVE THIS URL** - you need it for Postman environment

---

### Step 2.4: Set Required Scopes

1. In left sidebar, click **"OAuth & Permissions"**
2. Scroll to **"Scopes"** section → **"Bot Token Scopes"**
3. Verify these scopes are present:
   - `chat:write` (should be auto-added when you created webhook)
   - `commands` (should be auto-added when you created slash command)
4. If missing, click **"Add an OAuth Scope"** and add them

---

### Step 2.5: Install App to Workspace

1. In left sidebar, click **"Install App"**
2. Click **"Install to Workspace"** button
3. Review permissions screen:
   - Post messages to channels
   - Add slash commands
4. Click **"Allow"**
5. You should see:
   ```
   ✓ App successfully installed to [Your Workspace Name]
   ```

---

### Step 2.6: Verify Installation in Slack

1. Open **Slack desktop/web app**
2. Go to **#new-channel**
3. Type `/` (forward slash) in message box
4. You should see `/impact` appear in the slash command menu
5. If you see it, installation successful! ✅

---

## Part 3: Update Postman Environment

### Step 3.1: Add Slack Webhook URL

1. In Postman, go to **Environments**
2. Select your active environment
3. Find or add variable:
   - **Variable:** `SLACK_WEBHOOK_PM`
   - **Initial Value:** `https://hooks.slack.com/services/T.../B.../xxx` (from Step 2.3)
   - **Current Value:** (same)
   - **Type:** secret (recommended for webhooks)
4. Click **Save**

### Step 3.2: Verify All Required Variables

Make sure your environment has these variables set:

```
✅ ACTION_PUBLIC_URL = https://flows-action.postman.com/{your-id}
✅ SLACK_WEBHOOK_PM = https://hooks.slack.com/services/T.../B.../xxx
✅ GITHUB_TOKEN = ghp_... (with repo scope)
✅ REPO_OWNER = V-prajit (or your GitHub username)
✅ REPO_NAME = youareabsolutelyright
✅ RIPGREP_API_URL = http://localhost:3001
✅ SNOWFLAKE_ENDPOINT = http://localhost:8000/api/snowflake/generate-pr
```

---

## Part 4: Update Postman Flow (If Needed)

### Step 4.1: Verify Start Block

1. Open your Postman Flow
2. Click the **Start** block
3. Verify it can handle Slack's slash command payload format:
   ```json
   {
     "text": "fix mobile login",
     "user_id": "U123ABC",
     "user_name": "alice",
     "channel_id": "C456DEF",
     "channel_name": "new-channel"
   }
   ```
4. The important field is `text` - your flow should reference it as `{{Start.text}}`

### Step 4.2: Verify Slack Notification Block

1. Find your **Slack Notification** HTTP block (usually near the end)
2. Click on it to edit
3. Verify:
   - **Method:** POST
   - **URL:** `{{SLACK_WEBHOOK_PM}}`
   - **Body:** Your Block Kit JSON message
4. The URL MUST use the environment variable, not hardcoded

### Step 4.3: Add Immediate Response (Optional but Recommended)

Slack requires a response within 3 seconds. To avoid timeouts:

1. Right after **Start** block, add new **Send** block
2. Configure:
   - **Status Code:** 200
   - **Body:**
     ```json
     {
       "response_type": "in_channel",
       "text": "⏳ Processing your request: {{Start.text}}"
     }
     ```
3. Connect: `Start → Send → (rest of flow)`

This shows immediate feedback in Slack while your workflow runs.

---

## Part 5: Test the Integration

### Step 5.1: Start All Services

Open 2 terminals:

**Terminal 1: Backend (Snowflake)**
```bash
cd backend
python run.py
```
Wait for: `Server running on: http://localhost:8000`

**Terminal 2: Ripgrep API**
```bash
cd ripgrep-api
npm run dev
```
Wait for: `Server running on port 3001`

### Step 5.2: Verify Health

In a third terminal or browser:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

curl http://localhost:3001/api/health
# Should return: {"status":"ok",...}
```

### Step 5.3: Test in Slack

1. Go to **#new-channel** in Slack
2. Type test message:
   ```
   /impact test feature request
   ```
3. Press **Enter**

**Expected behavior:**
- Slack shows: "⏳ Processing your request: test feature request"
- (If you watch Postman Flows console, you'll see blocks executing)
- After ~30 seconds, notification appears in channel

### Step 5.4: Debug if Needed

**If command not recognized:**
- Reinstall Slack app (Part 2, Step 2.5)
- Verify command appears when you type `/` in Slack

**If "dispatch_failed" error:**
- Check Action URL is correct in slash command config
- Test Action URL with curl:
  ```bash
  curl -X POST https://flows-action.postman.com/{your-id} \
    -H "Content-Type: application/json" \
    -d '{"text":"test"}'
  ```

**If timeout after 3 seconds:**
- Add immediate response block (Part 4, Step 4.3)

**If no notification appears:**
- Check `SLACK_WEBHOOK_PM` is set correctly
- Test webhook directly:
  ```bash
  curl -X POST https://hooks.slack.com/services/T.../B.../xxx \
    -H "Content-Type: application/json" \
    -d '{"text":"test notification"}'
  ```
- Verify webhook was created for #new-channel (not a different channel)

**If Postman Flow errors:**
- Check Postman Flows console for error messages
- Verify all environment variables are set
- Check backend services are running

---

## Part 6: Full Demo Test

Now test the complete 3-person workflow:

### Test Scenario

1. **Customer posts complaint:**
   ```
   The mobile login page is broken! Can't sign in on iPhone 😡
   ```

2. **PM responds with command:**
   ```
   /impact fix mobile login responsive design
   ```

3. **Watch Postman Flows console:**
   - Ripgrep searches for "mobile login"
   - Checks open PRs
   - Calls Snowflake Cortex
   - Creates GitHub PR
   - Posts notification

4. **Engineer sees notification:**
   ```
   ✅ Task Created: fix-mobile-login
   Feature Request: fix mobile login responsive design
   Files Impacted: 2
   [View PR] button
   ```

5. **Click "View PR"** → Opens GitHub PR

**Success criteria:**
- ✅ Full workflow completes in 20-40 seconds
- ✅ GitHub PR is created with actual content
- ✅ Notification appears in same channel
- ✅ All 3 personas (customer, PM, engineer) visible in conversation

---

## Troubleshooting Guide

### Common Issues

#### Issue: "/impact command not showing"
**Symptoms:** Type `/` in Slack, don't see `/impact`

**Solutions:**
1. Check app is installed: Slack settings → Apps → Look for "PM Copilot"
2. Reinstall app: api.slack.com/apps → Your App → Install App → Reinstall
3. Check command was created: api.slack.com/apps → Your App → Slash Commands
4. Try in a different channel (permissions might differ)

---

#### Issue: "dispatch_failed" error
**Symptoms:** Slack shows red error: "dispatch_failed"

**Solutions:**
1. Verify Action URL is correct:
   - Go to api.slack.com/apps → Your App → Slash Commands
   - Check Request URL matches your Postman Action URL
2. Test Action URL with curl:
   ```bash
   curl -X POST {your-action-url} -d '{"text":"test"}'
   ```
3. Re-deploy Postman Flow:
   - Postman → Your Flow → Deploy → Save new URL
   - Update Slack slash command Request URL

---

#### Issue: Timeout after 3 seconds
**Symptoms:** Slack shows: "Operation timed out"

**Solutions:**
1. Add immediate response block (see Part 4, Step 4.3)
2. This responds to Slack immediately while workflow runs
3. Alternative: Use Slack's "Delayed Response" API (more complex)

---

#### Issue: No notification appears
**Symptoms:** Command works, but no message in channel

**Solutions:**
1. Check webhook URL:
   - Postman Environment → `SLACK_WEBHOOK_PM` → Verify URL
2. Test webhook directly:
   ```bash
   curl -X POST {your-webhook-url} \
     -H "Content-Type: application/json" \
     -d '{"text":"test"}'
   ```
3. Verify webhook is for #new-channel:
   - api.slack.com/apps → Your App → Incoming Webhooks
   - Check which channel the webhook posts to
4. Check Postman Flow Slack block:
   - URL should be `{{SLACK_WEBHOOK_PM}}`
   - NOT hardcoded URL

---

#### Issue: Postman Flow errors
**Symptoms:** Flow starts but blocks fail

**Solutions:**
1. Check Postman Flows console for error messages
2. Verify all services running:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:3001/api/health
   ```
3. Check environment variables are set:
   - `GITHUB_TOKEN`
   - `REPO_OWNER`
   - `REPO_NAME`
   - `RIPGREP_API_URL`
   - `SNOWFLAKE_ENDPOINT`
4. Test each service individually (see troubleshooting docs)

---

#### Issue: GitHub PR not created
**Symptoms:** Flow completes but no PR in GitHub

**Solutions:**
1. Check GitHub token:
   - github.com/settings/tokens
   - Verify token has `repo` scope
   - Generate new token if needed
2. Check repository name:
   - Verify `REPO_OWNER` and `REPO_NAME` are correct
3. Check Postman Flows console:
   - Look for GitHub API errors
   - Common: 404 (repo not found), 401 (auth failed)

---

## Security Considerations

### Webhook URL Security
- ⚠️ **Never commit webhook URLs to git**
- ✅ Use Postman environment variables (marked as "secret")
- ✅ Rotate webhooks if exposed
- ✅ Use separate webhooks for dev/prod

### Slack App Permissions
- ✅ Only grant necessary scopes (`chat:write`, `commands`)
- ✅ Don't request `admin` or `files:read` unless needed
- ✅ Review permissions before installing

### Token Management
- ⚠️ Never hardcode tokens in Postman collections
- ✅ Use environment variables
- ✅ Mark sensitive variables as "secret" type
- ✅ Rotate tokens regularly

---

## Next Steps

Once Slack integration works:

1. ✅ **Test multiple times** - Make sure it's reliable
2. ✅ **Practice demo** - Use `DEMO_SCRIPT_SLACK.md`
3. ✅ **Create backup materials** - Screenshots, video recording
4. ✅ **Document for judges** - Explain the workflow clearly
5. ⭐ **Agentverse deployment** - Your teammate handles bonus points

---

## Reference: Slack Slash Command Payload

When someone types `/impact fix mobile login`, Slack sends this to your Postman Action URL:

```json
{
  "token": "verification_token",
  "team_id": "T01ABC123",
  "team_domain": "your-workspace",
  "channel_id": "C01DEF456",
  "channel_name": "new-channel",
  "user_id": "U01GHI789",
  "user_name": "alice",
  "command": "/impact",
  "text": "fix mobile login",
  "api_app_id": "A01JKL012",
  "is_enterprise_install": "false",
  "response_url": "https://hooks.slack.com/commands/...",
  "trigger_id": "123456789.987654321.abcdef"
}
```

**Key fields your flow uses:**
- `text` - The feature request text
- `user_name` - Who triggered the command
- `channel_name` - Where it was triggered

---

## Reference: Environment Variables Checklist

| Variable | Example Value | Purpose |
|----------|--------------|---------|
| `ACTION_PUBLIC_URL` | `https://flows-action.postman.com/abc123` | Postman Flow endpoint |
| `SLACK_WEBHOOK_PM` | `https://hooks.slack.com/services/T.../B.../xxx` | Post to #new-channel |
| `GITHUB_TOKEN` | `ghp_xxxxxxxxxxxxxxxxxxxx` | Create PRs |
| `REPO_OWNER` | `V-prajit` | GitHub username |
| `REPO_NAME` | `youareabsolutelyright` | Repo name |
| `RIPGREP_API_URL` | `http://localhost:3001` | Code search |
| `SNOWFLAKE_ENDPOINT` | `http://localhost:8000/api/snowflake/generate-pr` | AI generation |

---

## Support Resources

- **Slack API Docs:** https://api.slack.com/slash-commands
- **Postman Flows Docs:** https://learning.postman.com/docs/postman-flows/
- **Postman Actions Docs:** https://learning.postman.com/docs/postman-flows/build-flows/actions/
- **Your Project README:** `README.md`
- **Demo Script:** `DEMO_SCRIPT_SLACK.md`

---

**Setup Complete! 🎉**

You're ready to demo the Customer → PM → Engineer workflow in Slack!

_Last updated: 2025-01-26_
