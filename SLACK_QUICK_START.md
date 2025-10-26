# Slack Integration - Quick Start Checklist

**Goal:** Get `/impact` working in 15 minutes

---

## ✅ Checklist

### Step 1: Deploy Postman Flow (5 min)
- [ ] Open Postman Desktop
- [ ] Go to Flows → Open your PM Copilot flow
- [ ] Click **"Deploy"** button (top right)
- [ ] Select **"Enable Public URL"**
- [ ] Copy the URL: `https://flows-action.postman.com/{id}`
- [ ] Save to Postman Environment:
  - Variable: `ACTION_PUBLIC_URL`
  - Value: (paste URL)

---

### Step 2: Create Slack App (5 min)
- [ ] Go to: https://api.slack.com/apps
- [ ] Click **"Create New App"** → **"From scratch"**
- [ ] App Name: `PM Copilot`
- [ ] Select your workspace
- [ ] Click **"Create App"**

---

### Step 3: Configure Slash Command (2 min)
- [ ] Left sidebar → **"Slash Commands"**
- [ ] Click **"Create New Command"**
- [ ] Command: `/impact`
- [ ] Request URL: (paste your Postman Action URL)
- [ ] Short Description: `Generate GitHub PR from feature request`
- [ ] Usage Hint: `[feature description]`
- [ ] Click **"Save"**

---

### Step 4: Enable Incoming Webhook (2 min)
- [ ] Left sidebar → **"Incoming Webhooks"**
- [ ] Toggle **ON**
- [ ] Click **"Add New Webhook to Workspace"**
- [ ] Select **#new-channel**
- [ ] Click **"Allow"**
- [ ] Copy webhook URL: `https://hooks.slack.com/services/T.../B.../xxx`
- [ ] Save to Postman Environment:
  - Variable: `SLACK_WEBHOOK_PM`
  - Value: (paste webhook URL)
  - Type: secret

---

### Step 5: Install App (1 min)
- [ ] Left sidebar → **"Install App"**
- [ ] Click **"Install to Workspace"**
- [ ] Click **"Allow"**
- [ ] Verify success message

---

### Step 6: Test in Slack (5 min)
- [ ] Start backend: `cd backend && python run.py`
- [ ] Start Ripgrep: `cd ripgrep-api && npm run dev`
- [ ] Open Slack → #new-channel
- [ ] Type: `/impact test feature request`
- [ ] Press Enter
- [ ] Wait ~30 seconds
- [ ] See notification in channel ✅

---

## 🚨 If Something Breaks

**Command not showing:**
→ Reinstall app: Slack API → Install App → Reinstall

**Timeout error:**
→ Add immediate response block in Postman Flow (see SLACK_SETUP.md Part 4.3)

**No notification:**
→ Check webhook URL is correct in Postman Environment

**Postman errors:**
→ Check Flows console for error messages

---

## 📋 Environment Variables (Postman)

Make sure these are set in your Postman Environment:

```
ACTION_PUBLIC_URL = https://flows-action.postman.com/{your-id}
SLACK_WEBHOOK_PM = https://hooks.slack.com/services/T.../B.../xxx
GITHUB_TOKEN = ghp_...
REPO_OWNER = V-prajit
REPO_NAME = youareabsolutelyright
RIPGREP_API_URL = http://localhost:3001
SNOWFLAKE_ENDPOINT = http://localhost:8000/api/snowflake/generate-pr
```

---

## 📖 Full Documentation

- **Detailed setup:** `SLACK_SETUP.md`
- **Demo script:** `DEMO_SCRIPT_SLACK.md`
- **Main README:** `README.md`

---

**Total Time: ~15 minutes**

Good luck! 🚀
