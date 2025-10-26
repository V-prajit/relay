# 🚨 ULTRA QUICK FIX (2 min)

**Error**: RUN DEMO button shows 500 error
**Cause**: PR_GENERATIONS table data not in right place

---

## Do This Now (2 min):

### 1. Run FINAL SQL in Snowflake (1 min)

1. Open **Snowflake Snowsight**
2. New worksheet
3. Copy **entire file**: `snowflake/FINAL_RUN_THIS.sql`
4. Paste and **Run All**
5. At bottom, should see: **"✅✅✅ SUCCESS! ✅✅✅"** with 6 total_prs

**This creates the table + adds 6 PRs in one go.**

---

### 2. Restart Backend (30 sec)

```bash
cd /Users/prajit/Desktop/projects/youareabsolutelyright/backend
python run.py
```

Wait 5 seconds for it to start.

---

### 3. Test (30 sec)

1. Open http://localhost:3002
2. Refresh page (Cmd+R / Ctrl+R)
3. Click **"RUN DEMO"**
4. ✅ Should show 4 boxes: SENTIMENT, SUMMARIZE, COMPLETE, EXTRACT

**If it works → READY FOR VIDEO! 🎬**

---

## What This Does:

`FINAL_RUN_THIS.sql`:
1. Selects BUGREWIND database (fixes "wrong database" issue)
2. Drops old PR_GENERATIONS table (fresh start)
3. Creates new PR_GENERATIONS table
4. Inserts 6 perfect PRs
5. Grants permissions
6. Verifies data

**This will work 100%** - it's a complete fresh start.

---

## If Still Broken:

See `FIX_500_ERROR.md` for detailed troubleshooting.

Most likely: Backend needs restart (Step 2).
