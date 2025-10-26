# Fix 500 Error on RUN DEMO Button

## Problem:
Backend error: `Object 'PR_GENERATIONS' does not exist or not authorized`

This means the SQL ran but **data is in wrong place** OR **didn't actually insert**.

---

## Solution (2 minutes):

### Step 1: Verify Data in Snowflake (1 min)

1. **Open Snowflake Snowsight**
2. **Create new worksheet**
3. **Copy/paste** `VERIFY_SNOWFLAKE.sql`
4. **Run All**

**Expected results**:
- Row count: **6**
- REPO_NAME: **V-prajit/postman-api-toolkit**

**If you see 6 rows** → Go to Step 2
**If you see 0 rows or error** → Go to Step 1b

---

### Step 1b: Re-run SQL (if data missing)

**IMPORTANT**: Select database FIRST!

1. **In Snowflake Snowsight**:
   - Click dropdown at top left (currently shows "No Database selected")
   - Select **BUGREWIND** database
   - Select **GIT_ANALYSIS** schema

2. **Create new worksheet**

3. **Copy/paste** entire file: `snowflake/populate_data_NO_COMMITS.sql`

4. **Run All** (Cmd+Enter / Ctrl+Enter)

5. **Check bottom** - should say "✅ Perfect demo data loaded!"

6. **Run verification query**:
   ```sql
   SELECT COUNT(*) as row_count FROM PR_GENERATIONS;
   ```
   Should return **6**

---

### Step 2: Restart Backend (30 sec)

The backend might be caching the "table doesn't exist" error.

```bash
cd /Users/prajit/Desktop/projects/youareabsolutelyright

# Kill and restart
lsof -ti:8000 | xargs kill -9
cd backend && python run.py &
cd ..
```

Wait 5 seconds for backend to start.

---

### Step 3: Test Dashboard (30 sec)

1. **Refresh dashboard**: http://localhost:3002 (Cmd+R / Ctrl+R)
2. **Click "RUN DEMO"**
3. **Should work now!** ✅

---

## If Still Failing:

### Check Backend Logs:

```bash
cd backend
python run.py
```

Look for errors about Snowflake connection or PR_GENERATIONS table.

**Common issues**:

1. **"Object 'PR_GENERATIONS' does not exist"**
   → Data not in BUGREWIND.GIT_ANALYSIS schema
   → Re-run SQL with database selected (Step 1b)

2. **"Not authorized"**
   → Check `.env` has `SNOWFLAKE_ROLE=ACCOUNTADMIN`
   → Run in Snowflake: `GRANT ALL ON TABLE PR_GENERATIONS TO ROLE ACCOUNTADMIN;`

3. **"Connection failed"**
   → Check `.env` has correct Snowflake credentials
   → Test: `curl http://localhost:8000/api/snowflake/health`

---

## Quick Fix Command (if you know data is there):

```bash
# Just restart backend
cd /Users/prajit/Desktop/projects/youareabsolutelyright/backend
python run.py
```

Then refresh dashboard and try RUN DEMO again.

---

## Success Checklist:

- [ ] Ran `VERIFY_SNOWFLAKE.sql` and saw 6 rows
- [ ] Backend restarted successfully
- [ ] Dashboard loads at http://localhost:3002
- [ ] Clicked RUN DEMO button
- [ ] 4 boxes populated (SENTIMENT, SUMMARIZE, COMPLETE, EXTRACT)

**If all checked → READY FOR VIDEO! 🎬**
