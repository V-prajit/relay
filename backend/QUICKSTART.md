# Phase 1 Quick Start (5 Minutes)

**TL;DR:** Get Elasticsearch running and test the indexing pipeline.

## Prerequisites
- Python 3.8+ with venv
- Git installed
- Internet connection

## Step 1: Get Elastic Credentials (First Time Only)

**Option A: Already have credentials?**
Skip to Step 2.

**Option B: Need to set up Elastic?**
Follow `SETUP_ELASTIC.md` (takes 10 minutes)

## Step 2: Configure Environment

```bash
cd backend

# Copy template
cp .env.example .env

# Edit .env and add your credentials:
# ELASTIC_API_KEY=your_key_here
# ELASTIC_ENDPOINT=https://your-project.es...
```

## Step 3: Install Dependencies

```bash
# Create + activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 4: Run Tests

```bash
python test_phase1.py
```

**Expected:** All tests pass in ~1-2 minutes.

## What Happens?

1. ✅ Connects to Elasticsearch
2. ✅ Creates `commits` index
3. ✅ Clones BentoML repo (small test)
4. ✅ Indexes 50 commits
5. ✅ Runs 3 search queries
6. ✅ Shows results

## Success Looks Like

```
✅ PASS - Elasticsearch Connection
✅ PASS - Index Creation
✅ PASS - Repository Indexing
✅ PASS - Basic Search

Results: 4/4 tests passed
🎉 Phase 1 Complete!
```

## Troubleshooting

**Connection failed?**
- Check `.env` has correct credentials
- Verify Elastic endpoint URL (starts with https://)
- Regenerate API key if needed

**Module not found?**
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**Clone failed?**
- Check internet connection
- GitHub might be rate-limiting (try again in 1 min)

## Next Steps

After tests pass:

```bash
# Commit your work
git add backend/
git commit -m "Phase 1: Elasticsearch indexing complete"

# Move to Phase 2
# See DEV_B.md for Phase 2 plan
```

## Files Created (Phase 1)

```
backend/
├── app/
│   ├── config.py              # Config management
│   ├── elastic/               # Elasticsearch integration
│   │   ├── client.py          # Connection
│   │   ├── schema.py          # Index mapping
│   │   └── indexer.py         # Bulk operations
│   └── git/                   # Git analysis
│       └── analyzer.py        # Commit extraction
├── test_phase1.py             # Test suite
├── PHASE1_README.md           # Full documentation
├── SETUP_ELASTIC.md           # Elastic setup guide
└── QUICKSTART.md              # This file
```

## Learn More

- **Full docs:** `PHASE1_README.md`
- **Elastic setup:** `SETUP_ELASTIC.md`
- **Summary:** `../PHASE1_SUMMARY.md`
- **Phase 2 plan:** `../DEV_B.md`

**Time to complete:** 5 min (if credentials ready) or 15 min (first-time setup)

---

**Questions?** Check the troubleshooting sections in the READMEs or review test output for error details.
