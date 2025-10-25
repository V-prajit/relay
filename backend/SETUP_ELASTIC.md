# Quick Start: Elasticsearch Serverless Setup

**Time needed:** 10-15 minutes

This guide walks you through setting up Elasticsearch Serverless for the first time.

## Step 1: Create Elastic Account

1. Go to **https://cloud.elastic.co/**
2. Click **"Start free trial"** or **"Sign up"**
3. Use your email or sign in with Google/GitHub
4. Complete email verification if required

## Step 2: Create Serverless Project

1. After logging in, click **"Create deployment"**
2. Select **"Serverless"** (NOT "Hosted Elasticsearch")
3. Choose project type: **"Elasticsearch"**
4. Configure:
   - **Name:** `bugrewind-dev` (or your choice)
   - **Cloud provider:** Any (GCP recommended for free tier)
   - **Region:** Choose closest to you (e.g., `us-central1`)
5. Click **"Create project"**
6. Wait 1-2 minutes for provisioning

## Step 3: Get Your Endpoint URL

1. Once project is ready, you'll see the **Overview** page
2. Find the **"Endpoint"** section
3. Copy the URL - it looks like:
   ```
   https://bugrewind-dev-abc123.es.us-central1.gcp.cloud.es.io
   ```
4. Save this for your `.env` file

## Step 4: Create API Key

1. In your project, open the menu (☰) on the left
2. Go to **Stack Management** → **API Keys**
3. Click **"Create API Key"**
4. Fill in:
   - **Name:** `BugRewind Development`
   - **Expiration:** None (or set to 1 year)
   - **Privileges:** Leave as "All" (we need full access)
5. Click **"Create API Key"**
6. **IMPORTANT:** Copy the **encoded** key immediately!
   - It looks like: `VnVhQ2ZHY0JDZGJrUW0tZTVhT3g6dWkybHAyYXhUTm1zeWFrdzl0dk5udw==`
   - You won't be able to see it again!
7. Save this key securely

## Step 5: Configure Your Project

1. Navigate to your `backend/` directory
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit `backend/.env` and add your credentials:
   ```env
   # Elasticsearch Configuration
   ELASTIC_API_KEY=VnVhQ2ZHY0JDZGJrUW0tZTVhT3g6dWkybHAyYXhUTm1zeWFrdzl0dk5udw==
   ELASTIC_ENDPOINT=https://bugrewind-dev-abc123.es.us-central1.gcp.cloud.es.io

   # Other settings (can leave as defaults)
   PORT=8000
   CLONE_DIR=/tmp/bugrewind-clones
   ```

4. Save the file

## Step 6: Install Dependencies

```bash
cd backend

# Create virtual environment (if you haven't)
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## Step 7: Test Connection

Run the Phase 1 test suite:

```bash
python test_phase1.py
```

**Expected first output:**
```
╔════════════════════════════════════════════════════════╗
║               PHASE 1 TEST SUITE                       ║
╚════════════════════════════════════════════════════════╝

TEST 1: Elasticsearch Connection
==========================================================
Connecting to: https://bugrewind-dev-abc123...
✅ Elasticsearch connection successful!
```

If you see ✅, you're all set! If you see ❌, check the troubleshooting below.

## 🐛 Troubleshooting

### ❌ "Missing configuration: ELASTIC_API_KEY"
- Make sure `.env` file exists in `backend/` directory
- Check that variable names match exactly (case-sensitive)
- No spaces around the `=` sign

### ❌ "Elasticsearch connection failed"
**Check endpoint URL:**
- Should start with `https://` (not `http://`)
- No trailing slash at the end
- Copy-paste directly from Elastic Console

**Check API key:**
- Should be the full encoded string
- No extra spaces or newlines
- Try regenerating a new key if issues persist

**Network issues:**
- Check your internet connection
- Try disabling VPN temporarily
- Check firewall settings

### ❌ "Authentication error"
- API key might be invalid or expired
- Go back to Step 4 and create a new API key
- Make sure you copied the **encoded** key, not the ID

### ⚠️  "Module not found: elasticsearch"
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`
- Check you're in the `backend/` directory

## 📊 Verify in Elastic Console (Optional)

You can also test the connection in Elastic's web interface:

1. Go to your Elastic Cloud Console
2. Open your project
3. Click **"Dev Tools"** in the left menu
4. In the Console, run:
   ```json
   GET /
   ```
5. You should see cluster info

## ✅ Success Checklist

- [ ] Elastic Serverless project created
- [ ] Endpoint URL copied to `.env`
- [ ] API key generated and copied to `.env`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test script passes connection test
- [ ] Ready to run full Phase 1 tests!

## 🚀 Next Steps

Once connection is working, run the full Phase 1 test suite:

```bash
python test_phase1.py
```

This will:
- Create the `commits` index
- Clone a test repository
- Index 50 commits
- Run search queries

See `PHASE1_README.md` for full details.

## 🆘 Still Having Issues?

Common fixes:
1. **Regenerate API key** - old one might be corrupted
2. **Check project status** - make sure it's running (not paused)
3. **Try different region** - some regions might have issues
4. **Use direct connection test:**
   ```python
   from elasticsearch import Elasticsearch
   es = Elasticsearch(
       "YOUR_ENDPOINT",
       api_key="YOUR_API_KEY"
   )
   print(es.ping())  # Should print: True
   ```

Need help? Check the Elastic documentation: https://www.elastic.co/guide/en/serverless/current/serverless-get-started.html
