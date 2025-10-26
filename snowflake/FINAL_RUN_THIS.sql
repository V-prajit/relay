-- ========================================
-- ⚡ FINAL FIX - RUN THIS IN SNOWFLAKE ⚡
-- ========================================
-- This will fix the "PR_GENERATIONS does not exist" error
-- Copy this ENTIRE file and paste in Snowflake Snowsight

-- STEP 1: SELECT DATABASE (CRITICAL!)
USE DATABASE BUGREWIND;
USE SCHEMA GIT_ANALYSIS;
USE WAREHOUSE BUGREWIND_WH;

SELECT '✅ Using correct database/schema' as status;

-- STEP 2: Check if table exists and clear it
DROP TABLE IF EXISTS PR_GENERATIONS CASCADE;

-- STEP 3: Create PR_GENERATIONS table
CREATE TABLE PR_GENERATIONS (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    FEATURE_REQUEST TEXT NOT NULL,
    PR_TITLE TEXT NOT NULL,
    PR_DESCRIPTION TEXT,
    BRANCH_NAME TEXT NOT NULL,
    IS_NEW_FEATURE BOOLEAN DEFAULT FALSE,
    REPO_NAME TEXT,
    MODEL_USED TEXT DEFAULT 'mistral-large',
    EXECUTION_TIME_MS NUMBER,
    GENERATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    IMPACTED_FILES VARIANT,
    CONFLICT_INFO TEXT
);

SELECT '✅ PR_GENERATIONS table created' as status;

-- STEP 4: Insert 6 perfect PRs
INSERT INTO PR_GENERATIONS (
    FEATURE_REQUEST,
    PR_TITLE,
    PR_DESCRIPTION,
    BRANCH_NAME,
    IS_NEW_FEATURE,
    REPO_NAME,
    MODEL_USED,
    EXECUTION_TIME_MS,
    GENERATED_AT
) VALUES
    (
        'add rate limiting middleware to prevent API abuse',
        'feat: Add rate limiting middleware',
        'Implemented express-rate-limit middleware to prevent API abuse. Configured 100 requests per 15 minutes per IP.',
        'feature/rate-limiting',
        TRUE,
        'V-prajit/postman-api-toolkit',
        'mistral-large',
        2134,
        DATEADD(hour, -3, CURRENT_TIMESTAMP())
    ),
    (
        'add JWT authentication for secure API access',
        'feat: Add JWT authentication',
        'Implemented JWT-based authentication using jsonwebtoken library. Added /auth/login and /auth/verify endpoints.',
        'feature/jwt-auth',
        TRUE,
        'V-prajit/postman-api-toolkit',
        'llama3-70b',
        3421,
        DATEADD(hour, -8, CURRENT_TIMESTAMP())
    ),
    (
        'fix request logger to include response time',
        'fix: Add response time to request logger',
        'Enhanced request logger middleware to track and log response times. Added color-coded output.',
        'fix/logger-response-time',
        FALSE,
        'V-prajit/postman-api-toolkit',
        'mistral-large',
        1876,
        DATEADD(hour, -12, CURRENT_TIMESTAMP())
    ),
    (
        'add CORS support for cross-origin requests',
        'feat: Add CORS middleware',
        'Implemented CORS middleware using cors package. Configured allowed origins, methods, and headers.',
        'feature/cors-support',
        TRUE,
        'V-prajit/postman-api-toolkit',
        'mixtral-8x7b',
        2567,
        DATEADD(day, -1, CURRENT_TIMESTAMP())
    ),
    (
        'add input validation for POST requests',
        'feat: Add request validation middleware',
        'Implemented express-validator for request body validation. Returns detailed validation errors.',
        'feature/input-validation',
        TRUE,
        'V-prajit/postman-api-toolkit',
        'mistral-large',
        2943,
        DATEADD(day, -2, CURRENT_TIMESTAMP())
    ),
    (
        'update health endpoint to include system metrics',
        'feat: Enhance health check endpoint',
        'Enhanced /health endpoint to return system uptime, memory usage, and Node.js version.',
        'feature/health-metrics',
        FALSE,
        'V-prajit/postman-api-toolkit',
        'llama3-70b',
        2198,
        DATEADD(day, -3, CURRENT_TIMESTAMP())
    );

SELECT '✅ 6 PRs inserted' as status;

-- STEP 5: Grant permissions
GRANT ALL ON TABLE PR_GENERATIONS TO ROLE ACCOUNTADMIN;

SELECT '✅ Permissions granted' as status;

-- STEP 6: Verify data
SELECT
    '✅✅✅ SUCCESS! ✅✅✅' as final_status,
    COUNT(*) as total_prs,
    ROUND(AVG(EXECUTION_TIME_MS), 0) as avg_time_ms,
    COUNT(DISTINCT MODEL_USED) as models_used
FROM PR_GENERATIONS;

-- STEP 7: Show all PRs
SELECT
    PR_TITLE,
    REPO_NAME,
    MODEL_USED,
    EXECUTION_TIME_MS,
    GENERATED_AT
FROM PR_GENERATIONS
ORDER BY GENERATED_AT DESC;

-- ========================================
-- ✅ DONE! Now restart backend:
-- cd backend && python run.py
-- Then open http://localhost:3002 and click RUN DEMO
-- ========================================
