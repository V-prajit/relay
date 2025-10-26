# Mock Repo Setup Instructions

## Quick Setup (10 minutes)

This creates a **postman-api-toolkit** GitHub repository for demo purposes.

---

## Step 1: Run Snowflake SQL (2 min)

### 1a. Fix COMMITS table
1. Open **Snowflake Snowsight**
2. Create new worksheet
3. Copy/paste **`snowflake/fix_commits_table.sql`**
4. Click **Run All** (Cmd+Enter / Ctrl+Enter)
5. Verify: Should say "COMMITS table created successfully"

### 1b. Populate perfect demo data
1. In same worksheet (or new one)
2. Copy/paste **`snowflake/populate_perfect_data.sql`**
3. Click **Run All**
4. Verify at bottom: Should say "✅ Perfect demo data loaded!"

**You should now have:**
- ✅ 6 PRs in PR_GENERATIONS table
- ✅ 8 commits in COMMITS table
- ✅ All for repo: `V-prajit/postman-api-toolkit`

---

## Step 2: Create GitHub Repo (3 min)

### Option A: Via GitHub Web UI (Easier)

1. Go to https://github.com/new
2. **Repository name**: `postman-api-toolkit`
3. **Description**: "Simple REST API testing toolkit - Postman + Snowflake demo"
4. **Public** repository (so judges can see it)
5. **DO NOT** initialize with README (we have one already)
6. Click **"Create repository"**

### Option B: Via GitHub CLI (Faster if installed)

```bash
cd mock-repo/postman-api-toolkit
gh repo create postman-api-toolkit --public --source=. --remote=origin --push
```

---

## Step 3: Push Code to GitHub (2 min)

```bash
# Navigate to mock repo
cd /Users/prajit/Desktop/projects/youareabsolutelyright/mock-repo/postman-api-toolkit

# Initialize git
git init
git add .
git commit -m "Initial commit: Basic Express API toolkit

- Health check endpoints (/health, /health/ready, /health/live)
- Echo service for request debugging
- User CRUD API with in-memory storage
- Request logger with color-coded output
- Complete API documentation"

# Add remote (replace V-prajit with your GitHub username if different)
git remote add origin https://github.com/V-prajit/postman-api-toolkit.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Verify**: Visit https://github.com/V-prajit/postman-api-toolkit - should show README and code

---

## Step 4: Create Sample PRs (Optional - 3 min)

If you want to show **real GitHub PRs** (not just Snowflake data):

### Create PR #1: Add rate limiting

```bash
cd /Users/prajit/Desktop/projects/youareabsolutelyright/mock-repo/postman-api-toolkit

# Create branch
git checkout -b feature/rate-limiting

# Create middleware file
cat > middleware/rateLimiter.js << 'EOF'
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests',
    message: 'Rate limit exceeded. Try again later.'
  }
});

module.exports = limiter;
EOF

# Commit and push
git add .
git commit -m "feat: Add rate limiting middleware

Implemented express-rate-limit to prevent API abuse
- 100 requests per 15 minutes per IP
- Custom rate limit exceeded response
- Ready to integrate into server.js"

git push origin feature/rate-limiting

# Create PR via GitHub CLI (or manually on GitHub)
gh pr create --title "feat: Add rate limiting middleware" --body "Prevents API abuse with 100 req/15min limit"
```

---

## Step 5: Update Backend Config (1 min)

Back in your main project:

```bash
cd /Users/prajit/Desktop/projects/youareabsolutelyright/backend
```

Edit `backend/.env` and change:
```env
# OLD
# REPO_NAME=youareabsolutelyright

# NEW
REPO_NAME=postman-api-toolkit
```

**Save the file.**

---

## Step 6: Restart Services (1 min)

```bash
# Kill existing processes
lsof -ti:8000,3001,3002 | xargs kill -9

# Start all services
cd /Users/prajit/Desktop/projects/youareabsolutelyright
./start-all.sh
```

---

## Step 7: Verify Everything (2 min)

1. **Open dashboard**: http://localhost:3002

2. **Check metrics**:
   - Total PRs: **6**
   - Cost Savings: **94%**
   - Avg Time: **~2,500ms**

3. **Click "RUN DEMO"**:
   - Should execute 4 Cortex functions
   - SENTIMENT, SUMMARIZE, COMPLETE, EXTRACT boxes populate

4. **Check Recent PRs section**:
   - Should show 6 PRs for `postman-api-toolkit`
   - "feat: Add rate limiting middleware" (newest)
   - "feat: Add JWT authentication"
   - etc.

5. **Check GitHub repo**:
   - Visit https://github.com/V-prajit/postman-api-toolkit
   - Should see README, code files, commits

---

## Troubleshooting

### "COMMITS table creation failed"
- Make sure you ran `fix_commits_table.sql` **before** `populate_perfect_data.sql`
- Check Snowflake role has CREATE TABLE permissions

### "No data showing on dashboard"
- Refresh page (Cmd+R / Ctrl+R)
- Check backend logs: `cd backend && python run.py`
- Verify data in Snowflake: `SELECT * FROM PR_GENERATIONS LIMIT 5;`

### "GitHub push failed"
- Check you created the repo first on GitHub
- Verify remote URL: `git remote -v`
- Update remote: `git remote set-url origin https://github.com/YOUR-USERNAME/postman-api-toolkit.git`

### "RUN DEMO button shows 500 error"
- Backend can't connect to Snowflake
- Check `backend/.env` has correct Snowflake credentials
- Test connection: `curl http://localhost:8000/api/snowflake/health`

---

## What You Now Have

✅ **GitHub Repo**: https://github.com/V-prajit/postman-api-toolkit
✅ **Snowflake Data**: 6 PRs + 8 commits for demo
✅ **Dashboard**: Shows real data from Snowflake
✅ **RUN DEMO**: Executes 4 Cortex LLM functions live
✅ **Realistic Use Case**: API toolkit fits Postman theme

---

## Next: Record Video Demo

See `VIDEO_DEMO_SCRIPT.md` for what to say and show!

**Estimated total time**: ~10 minutes to set everything up
