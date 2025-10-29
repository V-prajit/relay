# Digital Ocean Deployment Guide - Complete Setup

This guide will deploy your entire PM Copilot to Digital Ocean with permanent public URLs.

---

## Architecture Overview

**Before (Local + ngrok)**:
```
Slack → Postman Action → ngrok URLs (temporary) ❌
```

**After (Digital Ocean)**:
```
Slack → Postman Action → Digital Ocean URLs (permanent) ✅
```

**Services to Deploy**:
1. **Ripgrep API** (Node.js/Express) - Code search
2. **Backend** (Python/FastAPI) - Snowflake integration
3. **Frontend** (Next.js) - Dashboard

---

## Prerequisites

- [ ] Digital Ocean account (sign up at digitalocean.com)
- [ ] GitHub account with your repo pushed
- [ ] Snowflake credentials ready
- [ ] Claude API key
- [ ] GitHub token
- [ ] Slack webhook URL

---

## Cost Estimate

| Service | Digital Ocean Plan | Monthly Cost |
|---------|-------------------|--------------|
| Ripgrep API | Basic ($5) | $5 |
| Backend | Basic ($5) | $5 |
| Frontend | Basic ($5) or Vercel (free) | $5 or $0 |
| **Total** | | **$15 or $10/month** |

**Note**: Free $200 credit available for new DO accounts!

---

## Part 1: Prepare Code for Deployment

### Changes Needed

#### 1.1 Ripgrep API

**File**: `ripgrep-api/src/index.js`

**Current**:
```javascript
const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

**Change to**:
```javascript
const PORT = process.env.PORT || 3001;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

**File**: `ripgrep-api/package.json`

**Add**:
```json
{
  "engines": {
    "node": "18.x"
  },
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  }
}
```

#### 1.2 Backend (Python)

**File**: `backend/run.py` or `backend/app/main.py`

**Find**:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Change to**:
```python
import os
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

**File**: `backend/requirements.txt`

**Ensure these are present**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
snowflake-connector-python==3.6.0
python-dotenv==1.0.0
```

#### 1.3 Frontend (Next.js)

**File**: `frontend/package.json`

**Add**:
```json
{
  "engines": {
    "node": "18.x"
  },
  "scripts": {
    "build": "next build",
    "start": "next start",
    "dev": "next dev"
  }
}
```

**File**: `frontend/next.config.js`

**Add** (if not present):
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // For Docker deployment
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
}

module.exports = nextConfig
```

---

## Part 2: Deploy to Digital Ocean

### 2.1 Push Code to GitHub

**If not already done**:
```bash
cd /Users/prajit/Desktop/projects/youareabsolutelyright
git add .
git commit -m "Prepare for Digital Ocean deployment"
git push origin main
```

### 2.2 Deploy Ripgrep API

1. Go to https://cloud.digitalocean.com/apps
2. Click **Create App**
3. **Source**: Choose GitHub → Select your repo
4. **Source Directory**: `/ripgrep-api`
5. **App Type**: Web Service
6. **Build Command**: `npm install`
7. **Run Command**: `npm start`
8. **HTTP Port**: (leave empty, uses process.env.PORT)
9. **Environment Variables**: Add these:
   ```
   ALLOWED_ORIGINS=*
   NODE_ENV=production
   ```
10. **Name**: `ripgrep-api`
11. **Plan**: Basic ($5/month)
12. Click **Create Resources**

**Wait ~5 minutes for deployment**

13. Copy the URL: `https://ripgrep-api-xxxxx.ondigitalocean.app`

**Test**:
```bash
curl https://ripgrep-api-xxxxx.ondigitalocean.app/api/health
```

Expected: `{"status":"ok"}`

---

### 2.3 Deploy Backend (Snowflake)

1. Go to https://cloud.digitalocean.com/apps
2. Click **Create App**
3. **Source**: Same GitHub repo
4. **Source Directory**: `/backend`
5. **App Type**: Web Service
6. **Build Command**: `pip install -r requirements.txt`
7. **Run Command**: `python run.py` (or `uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
8. **HTTP Port**: (leave empty)
9. **Environment Variables**: Add ALL of these:
   ```
   SNOWFLAKE_ACCOUNT=MFFKJKS-EXB19493
   SNOWFLAKE_USER=RXH3770
   SNOWFLAKE_PASSWORD=Rabib12345678@
   SNOWFLAKE_DATABASE=BUGREWIND
   SNOWFLAKE_SCHEMA=GIT_ANALYSIS
   SNOWFLAKE_WAREHOUSE=BUGREWIND_WH
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   ENABLE_SNOWFLAKE=true
   ENABLE_CORTEX_LLM=true
   ```
10. **Name**: `backend-api`
11. **Plan**: Basic ($5/month)
12. Click **Create Resources**

**Wait ~5 minutes**

13. Copy URL: `https://backend-api-xxxxx.ondigitalocean.app`

**Test**:
```bash
curl https://backend-api-xxxxx.ondigitalocean.app/health
```

Expected: `{"status":"healthy"}`

---

### 2.4 Deploy Frontend (Alternative: Vercel - Recommended)

**Option A: Digital Ocean** ($5/month)

1. Create App → GitHub → `/frontend`
2. App Type: Static Site
3. Build Command: `npm run build`
4. Output Directory: `.next`
5. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://backend-api-xxxxx.ondigitalocean.app
   ```
6. Deploy

**Option B: Vercel** (FREE - Recommended for Next.js)

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Root Directory: `frontend`
4. Framework: Next.js (auto-detected)
5. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://backend-api-xxxxx.ondigitalocean.app
   ```
6. Deploy

**URL**: `https://your-app.vercel.app` or `https://frontend-xxxxx.ondigitalocean.app`

---

## Part 3: Update Postman Flow

### 3.1 Update Environment Variables

1. Open Postman Desktop
2. Go to **Environments**
3. Select `pm-copilot-dev` (or your environment)
4. Update these variables:

| Variable | Old Value | New Value |
|----------|-----------|-----------|
| `RIPGREP_API_URL` | `https://xxxx.ngrok.io` | `https://ripgrep-api-xxxxx.ondigitalocean.app` |
| `BACKEND_URL` | `http://localhost:8000` | `https://backend-api-xxxxx.ondigitalocean.app` |

5. Click **Save**

### 3.2 Update Flow Blocks

**If you have hardcoded URLs in blocks**:

1. Open your Postman Flow
2. Find HTTP blocks that call:
   - Ripgrep API
   - Backend/Snowflake API
3. Replace localhost/ngrok URLs with DO URLs
4. Example: Change `http://localhost:3001/api/search` to `https://ripgrep-api-xxxxx.ondigitalocean.app/api/search`

---

## Part 4: Test the Flow

### 4.1 Test Manually in Postman

1. Open your Postman Flow
2. Click **Run** (top right)
3. Input test data:
   ```json
   {
     "text": "Add dark mode toggle",
     "user_id": "@alice"
   }
   ```
4. Click **Run**

**Expected**:
- ✅ Ripgrep API called successfully
- ✅ Backend/Snowflake called successfully
- ✅ GitHub PR created (or content generated)
- ✅ Slack notification sent

**Check Console** for any errors.

---

## Part 5: Deploy Postman Action

### 5.1 Create Deployment

1. In Postman Flow, click **Deploy** (top right)
2. If first time:
   - Enable **"Request-triggered Action"**
   - Click **Create**
3. If already deployed:
   - Click **Create New Version**

**Result**: You'll get a permanent URL like:
```
https://flows-action.postman.com/abc123def456...
```

**⚠️ Important**: This URL stays the same across deployments!

### 5.2 Test Action Directly

```bash
curl -X POST https://flows-action.postman.com/abc123... \
  -H "Content-Type: application/json" \
  -d '{"text":"test feature","user_id":"@test"}'
```

Expected: Success response or flow execution

---

## Part 6: Update Slack Integration

### 6.1 Update Slash Command

1. Go to https://api.slack.com/apps
2. Select your app: **PM Copilot**
3. Click **Slash Commands** (left sidebar)
4. Click your `/impact` command
5. **Update Request URL**:
   - Old: `https://xxxx.ngrok.io`
   - New: `https://flows-action.postman.com/abc123...`
6. Click **Save**

### 6.2 Test in Slack

1. Open Slack workspace
2. Go to channel with bot
3. Type:
   ```
   /impact "Add OAuth login support"
   ```
4. Press Enter

**Expected** (within 30-60 seconds):
- ✅ Slack shows acknowledgment
- ✅ Notification appears with PR details
- ✅ GitHub PR created
- ✅ Reasoning trace visible

---

## Part 7: Verify Everything Works

### 7.1 End-to-End Test

**Scenario**: New Feature Request

1. **Slack**: `/impact "Add rate limiting middleware"`
2. **Flow Execution**:
   - Ripgrep API searches for "rate limiting"
   - Backend generates PR with Snowflake Cortex
   - GitHub API creates PR
   - Slack webhook sends notification
3. **Check**:
   - Slack message received ✅
   - GitHub PR exists ✅
   - Dashboard shows execution (if deployed) ✅

### 7.2 Check Logs

**Digital Ocean**:
1. Go to Apps → Your App
2. Click **Runtime Logs**
3. Check for errors

**Postman**:
1. Open Flow → Console
2. Check execution history
3. Look for failed API calls

---

## Troubleshooting

### Issue: Ripgrep API 502 Error

**Symptom**: `502 Bad Gateway` when calling ripgrep API

**Solutions**:
1. Check DO app is running (not crashed)
2. Check logs for errors
3. Verify `PORT` is using `process.env.PORT`
4. Check `package.json` has `"start": "node src/index.js"`

**Debug**:
```bash
# Check health endpoint
curl https://ripgrep-api-xxxxx.ondigitalocean.app/api/health
```

---

### Issue: Backend 500 Error

**Symptom**: Backend returns 500 Internal Server Error

**Solutions**:
1. Check Snowflake credentials in environment variables
2. Verify all env vars are set (check DO dashboard)
3. Check logs: "Connection to Snowflake failed"
4. Test Snowflake credentials locally first

**Debug**:
```bash
curl https://backend-api-xxxxx.ondigitalocean.app/health
curl https://backend-api-xxxxx.ondigitalocean.app/api/snowflake/health
```

---

### Issue: CORS Errors

**Symptom**: Postman Action fails with CORS error

**Solutions**:
1. Update CORS in ripgrep-api:
   ```javascript
   app.use(cors({
     origin: '*', // Or specific Postman domains
     methods: ['GET', 'POST', 'OPTIONS'],
   }));
   ```
2. Redeploy ripgrep-api
3. Check backend has CORS enabled

---

### Issue: Postman Action Timeout

**Symptom**: Action times out after 30 seconds

**Solutions**:
1. Check DO apps are responding quickly
2. Optimize API response times
3. Consider adding immediate Slack response in flow
4. Check for infinite loops in flow

---

### Issue: Environment Variables Not Working

**Symptom**: "Environment variable not found"

**Solutions**:
1. In DO dashboard → App → Settings → Environment Variables
2. Ensure all variables are added
3. Click **Save** and wait for redeployment
4. Check logs to verify variables are loaded

---

## Monitoring & Maintenance

### Check App Health

**Digital Ocean**:
- Apps Dashboard shows uptime
- Runtime Logs show errors
- Metrics show request volume

**Postman**:
- Flow Analytics show execution count
- Console shows failed requests
- Environment variables are synced

### Update Apps

**To update after code changes**:
1. Push changes to GitHub
2. DO automatically rebuilds and deploys
3. Or manually trigger: Apps → Your App → "Force Rebuild"

### Scale Apps

**If needed**:
1. Apps → Your App → Settings
2. Change Plan (Basic → Professional)
3. Increase resource limits
4. Add multiple instances (scaling)

---

## Cost Optimization

### Free Options

- ✅ **Frontend**: Deploy to Vercel (free)
- ✅ **Postman Actions**: Included in Flows add-on
- ✅ **GitHub**: Free for public repos

### Keep Costs Low

- Use Basic plan ($5/month per app)
- Deploy frontend to Vercel (free)
- Monitor usage to avoid overages
- Use DO $200 free credit

**Monthly Cost**: $10-15 with optimizations

---

## Deployment Checklist

### Pre-Deployment
- [ ] Code changes made (PORT configurations)
- [ ] GitHub repo updated
- [ ] Snowflake credentials ready
- [ ] DO account created

### During Deployment
- [ ] Ripgrep API deployed to DO
- [ ] Backend deployed to DO
- [ ] Frontend deployed to DO/Vercel
- [ ] All apps show "Active" status
- [ ] Health endpoints respond

### Post-Deployment
- [ ] Postman environment updated with DO URLs
- [ ] Flow tested manually
- [ ] Action deployed with permanent URL
- [ ] Slack slash command updated
- [ ] End-to-end test successful

### Verification
- [ ] `/impact` command works in Slack
- [ ] GitHub PR created successfully
- [ ] Slack notification received
- [ ] Dashboard shows execution (if deployed)
- [ ] No errors in DO logs

---

## URLs Reference

**After deployment, update this with your actual URLs**:

```
Ripgrep API:  https://ripgrep-api-xxxxx.ondigitalocean.app
Backend:      https://backend-api-xxxxx.ondigitalocean.app
Frontend:     https://your-app.vercel.app
Postman Action: https://flows-action.postman.com/abc123...
```

---

## Support & Resources

**Digital Ocean**:
- Docs: https://docs.digitalocean.com/products/app-platform/
- Support: https://www.digitalocean.com/support/

**Postman**:
- Flows Docs: https://learning.postman.com/docs/postman-flows/
- Actions: https://learning.postman.com/docs/postman-flows/build-flows/actions/

**This Project**:
- README.md - Project overview
- CLAUDE.md - Developer instructions
- SETUP.md - Local setup guide

---

**Deployment Complete! 🚀**

Your PM Copilot is now running on permanent public URLs and ready for production use.

*From localhost to production in 30 minutes.*
