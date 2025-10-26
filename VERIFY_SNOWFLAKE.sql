-- ========================================
-- VERIFY SNOWFLAKE DATA EXISTS
-- ========================================
-- Run this in Snowflake to check if data is there

-- 1. Check which database/schema you're in
SELECT CURRENT_DATABASE() as current_db, CURRENT_SCHEMA() as current_schema;

-- 2. Switch to correct database/schema (MUST DO THIS!)
USE DATABASE BUGREWIND;
USE SCHEMA GIT_ANALYSIS;

-- 3. Check if PR_GENERATIONS table exists
SHOW TABLES LIKE 'PR_GENERATIONS';

-- 4. Count rows in PR_GENERATIONS
SELECT COUNT(*) as row_count FROM PR_GENERATIONS;

-- 5. View all PRs
SELECT
    PR_TITLE,
    REPO_NAME,
    MODEL_USED,
    GENERATED_AT
FROM PR_GENERATIONS
ORDER BY GENERATED_AT DESC;

-- ========================================
-- EXPECTED RESULTS:
-- ========================================
-- - Row count should be 6
-- - REPO_NAME should be 'V-prajit/postman-api-toolkit'
-- - Should see 6 different PR titles
--
-- If row_count = 0 or table doesn't exist:
--   → Re-run populate_data_NO_COMMITS.sql
--   → Make sure you SELECT the BUGREWIND database first!
