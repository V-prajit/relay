# PM Copilot - Slack Socket Mode Listener

**No public URL required!** This app uses Slack Socket Mode to listen for `/impact` commands and process them entirely on localhost.

## What This Does

Customer complains in #new-channel → PM types `/impact "fix mobile login"` → This app:
1. Searches codebase with Ripgrep API (localhost:3001)
2. Generates PR with Snowflake Cortex (localhost:8000)
3. (Optionally) Creates GitHub PR
4. Posts rich notification back to Slack

**All running on your machine - no deployment needed!**

## Quick Start

### 1. Install Dependencies
```bash
cd slack-listener
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Slack tokens (see Setup Guide below)
```

### 3. Start the Listener
```bash
npm start
```

### 4. Use in Slack
In #new-channel:
```
/impact fix mobile login responsive design
```

Wait ~30 seconds → See notification! ✅

---

## Setup Guide

See **`../SLACK_SOCKET_MODE_SETUP.md`** for complete step-by-step instructions including:
- Creating Slack App with Socket Mode
- Getting Bot Token and App Token
- Configuring slash command
- Testing end-to-end

---

## Environment Variables

| Variable | Example | Required | Description |
|----------|---------|----------|-------------|
| `SLACK_BOT_TOKEN` | `xoxb-...` | ✅ Yes | From OAuth & Permissions |
| `SLACK_APP_TOKEN` | `xapp-...` | ✅ Yes | From Basic Information |
| `RIPGREP_API_URL` | `http://localhost:3001` | ✅ Yes | Ripgrep API endpoint |
| `BACKEND_API_URL` | `http://localhost:8000` | ✅ Yes | Snowflake backend |
| `GITHUB_TOKEN` | `ghp_...` | ⭐ Optional | For auto PR creation |
| `REPO_OWNER` | `V-prajit` | ⭐ Optional | GitHub repo owner |
| `REPO_NAME` | `youareabsolutelyright` | ⭐ Optional | GitHub repo name |
| `AUTO_CREATE_PR` | `false` | ⭐ Optional | Set to `true` to enable |

---

## Running the Full Stack

You need 3 terminals:

**Terminal 1: Backend (Snowflake Cortex)**
```bash
cd backend
python run.py
# Wait for: Server running on: http://localhost:8000
```

**Terminal 2: Ripgrep API**
```bash
cd ripgrep-api
npm run dev
# Wait for: Server running on port 3001
```

**Terminal 3: Slack Listener (this app)**
```bash
cd slack-listener
npm start
# Wait for: ⚡️ PM Copilot Slack Listener (Socket Mode)
```

---

## Testing

### Quick Health Check
```bash
# Test backend
curl http://localhost:8000/health

# Test ripgrep
curl http://localhost:3001/api/health

# Test Slack listener (check console output)
# Should show: "Listening for /impact commands in Slack..."
```

### Test in Slack
1. Go to #new-channel
2. Type: `/impact test feature request`
3. Check console output for step-by-step progress
4. Wait ~30 seconds
5. See notification in channel ✅

---

## Troubleshooting

### "Command not recognized"
- Make sure Slack app is installed to workspace
- Verify slash command is configured (no Request URL needed for Socket Mode!)
- Reinstall app if needed

### "Connection error" or "socket mode error"
- Check `SLACK_APP_TOKEN` is correct (starts with `xapp-`)
- Verify Socket Mode is enabled in Slack app settings
- Make sure app has `connections:write` scope

### "Service unavailable"
- Check backend is running: `curl http://localhost:8000/health`
- Check ripgrep is running: `curl http://localhost:3001/api/health`
- Verify URLs in `.env` match your running services

### "GitHub PR creation failed"
- This is optional - workflow continues without it
- Check `GITHUB_TOKEN` has `repo` scope
- Verify branch doesn't already exist
- Set `AUTO_CREATE_PR=false` to disable

---

## Logs

The app logs each step:
```
📨 Received /impact command from @alice
Feature request: "fix mobile login"
====================================

🔍 Step 1: Searching codebase with Ripgrep...
   ✅ Found 2 file(s)
   📁 Files: Login.tsx, mobile.css

🤖 Step 2: Generating PR with Snowflake Cortex...
   ✅ Generated PR: "fix: Mobile login responsive design"
   🌿 Branch: fix/mobile-login-20250126-abc123

💬 Step 3: Sending notification to Slack...
   ✅ Notification sent to Slack!

✅ WORKFLOW COMPLETE!
```

---

## Advantages of Socket Mode

✅ **No public URL required** - Works entirely on localhost
✅ **No ngrok needed** - No tunneling services
✅ **Faster** - No cloud round-trip
✅ **More reliable** - Direct WebSocket connection
✅ **Free** - No paid tunnel/hosting services
✅ **Secure** - Services stay on your machine

---

## For Deployment (Optional)

If you want to deploy this to production later:
- Deploy to Heroku, Railway, or DigitalOcean
- Socket Mode still works! (app connects to Slack via WebSocket)
- No need to expose public URLs for your backend services
- More info: https://api.slack.com/apis/socket-mode

---

## Support

- **Setup Guide:** `../SLACK_SOCKET_MODE_SETUP.md`
- **Demo Script:** `../DEMO_SCRIPT_SLACK.md` (update for Socket Mode)
- **Slack Socket Mode Docs:** https://api.slack.com/apis/socket-mode
- **Slack Bolt SDK:** https://slack.dev/bolt-js/

---

**Built with:**
- [@slack/bolt](https://www.npmjs.com/package/@slack/bolt) - Slack SDK with Socket Mode
- [axios](https://www.npmjs.com/package/axios) - HTTP client
- [dotenv](https://www.npmjs.com/package/dotenv) - Environment variables

**License:** MIT
