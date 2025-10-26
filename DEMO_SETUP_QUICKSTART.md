# 🚀 Demo Setup Quickstart (10 min)

**Goal**: Get dashboard perfect for video recording + create GitHub repo

---

## Step 1: Fix Snowflake (3 min) ⚡

### 1.1 Create COMMITS Table
1. Open **Snowflake Snowsight** (web UI)
2. Click **"Worksheets"** → **"+"** (new worksheet)
3. Copy **entire contents** of `snowflake/fix_commits_table.sql`
4. Paste and click **"Run All"**
5. ✅ Should see: "COMMITS table created successfully"

### 1.2 Add Perfect Demo Data
1. Same worksheet (or new one)
2. Copy **entire contents** of `snowflake/populate_perfect_data.sql`
3. Paste and click **"Run All"**
4. ✅ Should see at bottom: "✅ Perfect demo data loaded!"

**You now have**: 6 PRs + 8 commits in Snowflake

---

## Step 2: Create GitHub Repo (3 min) 📦

### Via GitHub Web:
1. Go to https://github.com/new
2. Name: **`postman-api-toolkit`**
3. Description: "REST API testing toolkit - Postman + Snowflake demo"
4. **Public** repo
5. **Do NOT initialize** with README
6. Click **"Create repository"**

### Push Code:
```bash
cd /Users/prajit/Desktop/projects/youareabsolutelyright/mock-repo/postman-api-toolkit

git init
git add .
git commit -m "Initial commit: Express API toolkit with health, echo, users endpoints"
git branch -M main
git remote add origin https://github.com/V-prajit/postman-api-toolkit.git
git push -u origin main
```

✅ Visit https://github.com/V-prajit/postman-api-toolkit - should show code

---

## Step 3: Restart Dashboard (2 min) 🔄

```bash
cd /Users/prajit/Desktop/projects/youareabsolutelyright

# Kill existing servers
lsof -ti:8000,3001,3002 | xargs kill -9

# Start all
./start-all.sh
```

Wait 10 seconds, then open: http://localhost:3002

---

## Step 4: Verify Everything (2 min) ✅

### Dashboard Should Show:
- **Total PRs**: 6
- **Cost Savings**: 94%
- **Avg Time**: ~2,500ms
- **Active Models**: Mistral-Large (ACTIVE), Llama 3 70B, Mixtral 8x7B

### Test RUN DEMO:
1. Click **"RUN DEMO"** button (center column)
2. Wait 5-10 seconds
3. ✅ Should see 4 boxes populate:
   - SENTIMENT: Score like `0.65`
   - SUMMARIZE: Text summary
   - COMPLETE: LLM explanation
   - EXTRACT: Extracted answer

### Check Recent PRs (right column):
Should show 6 PRs:
- "feat: Add rate limiting middleware" (3 hours ago)
- "feat: Add JWT authentication" (8 hours ago)
- "fix: Add response time to request logger" (12 hours ago)
- "feat: Add CORS middleware" (1 day ago)
- "feat: Add request validation middleware" (2 days ago)
- "feat: Enhance health check endpoint" (3 days ago)

---

## Step 5: Record Video (See VIDEO_DEMO_SCRIPT.md)

**Dashboard is now LIVE and perfect for recording!**

---

## Quick Troubleshooting

### "RUN DEMO shows 500 error"
```bash
# Restart backend
cd backend
python run.py
```

### "Dashboard shows 0 PRs"
- Refresh page (Cmd+R / Ctrl+R)
- Verify Snowflake data: Run `SELECT COUNT(*) FROM PR_GENERATIONS;` in Snowflake
- Check backend logs for Snowflake connection errors

### "GitHub push failed"
```bash
# Check remote
git remote -v

# If wrong, update:
git remote set-url origin https://github.com/YOUR-USERNAME/postman-api-toolkit.git
git push -u origin main
```

---

## Files Created Summary

| File | Purpose |
|------|---------|
| `snowflake/fix_commits_table.sql` | Creates COMMITS table |
| `snowflake/populate_perfect_data.sql` | Adds 6 PRs + 8 commits |
| `mock-repo/postman-api-toolkit/` | Complete Node.js API toolkit |
| `mock-repo/SETUP.md` | Detailed setup guide |
| `VIDEO_DEMO_SCRIPT.md` | What to say/show in video |
| `backend/.env` | Updated with `REPO_NAME=postman-api-toolkit` |

---

## Next Steps

1. ✅ Snowflake tables populated
2. ✅ GitHub repo created
3. ✅ Dashboard running with perfect data
4. 🎬 **Record video demo** (see VIDEO_DEMO_SCRIPT.md)
5. 📤 **Upload to YouTube + submit**

**Total setup time**: ~10 minutes
**Video recording time**: ~10 minutes (including retakes)
**Total**: ~20 minutes to complete submission 🚀
