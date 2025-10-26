# ❄️ Snowflake Cortex Analytics Hub - Quick Reference Card

## ⚠️ FIRST TIME SETUP (Do This Once!)

**Before starting the dashboard**, create Snowflake tables:

1. Open Snowflake Snowsight (web UI)
2. Create new worksheet
3. Copy/paste contents of `snowflake/setup_tables.sql`
4. Run all (Cmd+Enter / Ctrl+Enter)
5. Verify: Should create PR_GENERATIONS and COMMITS tables with sample data

**See `snowflake/README.md` for detailed setup instructions.**

Without this step, you'll get:
- ❌ "Table does not exist" when uploading YAML
- ❌ 500 error when clicking "RUN DEMO" button

---

## One-Line Commands

```bash
# Start everything
./start-all.sh

# Stop everything
./stop-all.sh

# Test everything
./test-dashboard.sh
```

## URLs

- **Snowflake Cortex Hub**: http://localhost:3002 ⭐ (MAIN SHOWCASE)
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health
- **Snowflake Health**: http://localhost:8000/api/snowflake/health
- **Cortex Features**: http://localhost:8000/api/cortex-showcase/features-summary

## Key Endpoints (for testing)

```bash
# Snowflake Features Summary (SHOW THIS TO JUDGES!)
curl http://localhost:8000/api/cortex-showcase/features-summary

# Cortex LLM Functions Demo (4 functions)
curl http://localhost:8000/api/cortex-showcase/llm-functions/demo

# Time Travel (24 hours ago)
curl -X POST http://localhost:8000/api/cortex-showcase/time-travel \
  -H "Content-Type: application/json" \
  -d '{"hours_ago": 24, "query_type": "pr_generations"}'

# Cortex Search (Semantic)
curl -X POST http://localhost:8000/api/cortex-showcase/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication bug", "limit": 10}'

# Snowflake Health
curl http://localhost:8000/api/snowflake/health
```

## Troubleshooting One-Liners

```bash
# Kill stuck processes
lsof -ti:8000,3001,3002 | xargs kill -9

# Check what's running
lsof -i :8000,3001,3002

# View logs
tail -f logs/*.log

# Restart just backend
cd backend && python run.py

# Restart just ripgrep
cd ripgrep-api && npm run dev

# Restart just frontend
cd frontend && npm run dev
```

## Demo Script for Snowflake Judges (60 seconds)

1. **Open dashboard**: http://localhost:3002
2. **Point to header**: "Snowflake Cortex Analytics Hub - all AI inside Snowflake"
3. **Point to green badge**: "Connected to BUGREWIND database, version 9.33.1"
4. **Click "Run Live Demo"**: Shows 4 Cortex LLM functions (SENTIMENT, SUMMARIZE, COMPLETE, EXTRACT_ANSWER)
5. **Point to cost savings**: "94% cheaper - $0.001 vs $0.015 per call"
6. **Click "24h Ago"**: Time Travel demo - unique to Snowflake!
7. **Point to data warehouse**: "All PRs stored for analytics & audit"
8. **Scroll to talking points**: "Production-ready, no external APIs"

## Key Files

```
start-all.sh                                  # Start script
stop-all.sh                                   # Stop script
SNOWFLAKE_SHOWCASE_COMPLETE.md                # MAIN GUIDE (read this!)
QUICK_REFERENCE.md                            # This file
backend/app/routes/cortex_showcase.py         # Snowflake demo endpoints
snowflake/cortex_analyst_semantic_model.yaml  # Upload to Snowflake
frontend/app/page.tsx                         # Snowflake Cortex Hub UI
```

## Port Reference

- **8000**: Backend API (Python/FastAPI)
- **3001**: Ripgrep API (Node.js)
- **3002**: Dashboard UI (Next.js)

## Stack (Snowflake-First!)

- **🎯 AI & Data Warehouse**: Snowflake Cortex (Mistral-Large, Llama, Mixtral)
- **🎯 Data Storage**: Snowflake (PR_GENERATIONS, COMMITS, BUG_ANALYSIS tables)
- **🎯 Time Travel**: Snowflake (unique feature - no competitor has this)
- **Frontend**: Next.js 16 + React 19 + TailwindCSS 4 (Snowflake-branded UI)
- **Backend**: FastAPI + Snowflake Connector
- **Orchestration**: Postman AI Agent (calls Snowflake for execution)
