# Slack Socket Mode - Quick Start (20 Minutes)

**No public URL required!** Everything runs on localhost.

---

## ✅ Checklist

### Part 1: Create Slack App (10 min)

- [ ] Go to https://api.slack.com/apps → Create New App → From scratch
- [ ] Name: `PM Copilot`, select your workspace
- [ ] **Socket Mode** → Toggle ON → Generate token → Save `SLACK_APP_TOKEN` (xapp-...)
- [ ] **OAuth & Permissions** → Bot Token Scopes → Add: `chat:write`, `commands`, `users:read`
- [ ] **OAuth & Permissions** → Install to Workspace → Save `SLACK_BOT_TOKEN` (xoxb-...)
- [ ] **Slash Commands** → Create `/impact` (Request URL doesn't matter!)
- [ ] Verify: Type `/` in #new-channel → See `/impact` ✅

---

### Part 2: Configure App (5 min)

```bash
cd slack-listener
npm install
cp .env.example .env
```

**Edit .env:**
```bash
SLACK_BOT_TOKEN=xoxb-YOUR-TOKEN-HERE
SLACK_APP_TOKEN=xapp-YOUR-TOKEN-HERE
RIPGREP_API_URL=http://localhost:3001
BACKEND_API_URL=http://localhost:8000
AUTO_CREATE_PR=false
```

---

### Part 3: Start Services (5 min)

**Terminal 1: Backend**
```bash
cd backend
python run.py
```

**Terminal 2: Ripgrep**
```bash
cd ripgrep-api
npm run dev
```

**Terminal 3: Slack Listener**
```bash
cd slack-listener
npm start
```

Wait for: "⚡️ PM Copilot Slack Listener (Socket Mode) - Status: RUNNING ✅"

---

### Part 4: Test (1 min)

In #new-channel:
```
/impact fix mobile login responsive design
```

**Expected:**
- Immediate: "⏳ Processing..."
- After ~30 seconds: Rich notification with files, branch, PR preview ✅

---

## 🐛 Quick Fixes

**Command not showing:** Reinstall app (OAuth & Permissions → Reinstall)

**Connection failed:** Check `SLACK_APP_TOKEN` is correct (xapp-...)

**Services unavailable:**
```bash
curl http://localhost:8000/health
curl http://localhost:3001/api/health
```

---

## 📖 Full Guide

See **SLACK_SOCKET_MODE_SETUP.md** for:
- Detailed explanations
- Troubleshooting guide
- Demo script
- Environment variables reference

---

**Total time:** 20 minutes
**Result:** Fully working PM Copilot on localhost! 🚀
