-- ========================================
-- SIMPLIFIED: PR Data Only (No COMMITS Table)
-- ========================================
-- Use this if COMMITS table creation is failing
-- Dashboard RUN DEMO button will still work perfectly!

USE DATABASE BUGREWIND;
USE SCHEMA GIT_ANALYSIS;
USE WAREHOUSE BUGREWIND_WH;

-- ========================================
-- CLEAR OLD PR DATA
-- ========================================

DELETE FROM PR_GENERATIONS;

-- ========================================
-- INSERT 6 PERFECT PRS
-- ========================================

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
    -- PR #1: Rate limiting (NEW FEATURE)
    (
        'add rate limiting middleware to prevent API abuse',
        'feat: Add rate limiting middleware',
        'Implemented express-rate-limit middleware to prevent API abuse. Configured 100 requests per 15 minutes per IP. Added custom rate limit exceeded response with Retry-After header.',
        'feature/rate-limiting',
        TRUE,
        'V-prajit/postman-api-toolkit',
        'mistral-large',
        2134,
        DATEADD(hour, -3, CURRENT_TIMESTAMP())
    ),

    -- PR #2: JWT auth (NEW FEATURE)
    (
        'add JWT authentication for secure API access',
        'feat: Add JWT authentication',
        'Implemented JWT-based authentication using jsonwebtoken library. Added /auth/login and /auth/verify endpoints. Protected routes require Bearer token in Authorization header.',
        'feature/jwt-auth',
        TRUE,
        'V-prajit/postman-api-toolkit',
        'llama3-70b',
        3421,
        DATEADD(hour, -8, CURRENT_TIMESTAMP())
    ),

    -- PR #3: Request logger fix (UPDATE)
    (
        'fix request logger to include response time',
        'fix: Add response time to request logger',
        'Enhanced request logger middleware to track and log response times. Added color-coded output for different HTTP status codes. Improved log formatting for better readability.',
        'fix/logger-response-time',
        FALSE,
        'V-prajit/postman-api-toolkit',
        'mistral-large',
        1876,
        DATEADD(hour, -12, CURRENT_TIMESTAMP())
    ),

    -- PR #4: CORS support (NEW FEATURE)
    (
        'add CORS support for cross-origin requests',
        'feat: Add CORS middleware',
        'Implemented CORS middleware using cors package. Configured allowed origins, methods, and headers. Added preflight request handling for complex requests.',
        'feature/cors-support',
        TRUE,
        'V-prajit/postman-api-toolkit',
        'mixtral-8x7b',
        2567,
        DATEADD(day, -1, CURRENT_TIMESTAMP())
    ),

    -- PR #5: Input validation (NEW FEATURE)
    (
        'add input validation for POST requests',
        'feat: Add request validation middleware',
        'Implemented express-validator for request body validation. Added schema validation for /users endpoints. Returns detailed validation errors with 400 status code.',
        'feature/input-validation',
        TRUE,
        'V-prajit/postman-api-toolkit',
        'mistral-large',
        2943,
        DATEADD(day, -2, CURRENT_TIMESTAMP())
    ),

    -- PR #6: Health endpoint enhancement (UPDATE)
    (
        'update health endpoint to include system metrics',
        'feat: Enhance health check endpoint',
        'Enhanced /health endpoint to return system uptime, memory usage, and Node.js version. Added /health/ready for readiness probe. Implemented /health/live for liveness probe.',
        'feature/health-metrics',
        FALSE,
        'V-prajit/postman-api-toolkit',
        'llama3-70b',
        2198,
        DATEADD(day, -3, CURRENT_TIMESTAMP())
    );

-- ========================================
-- VERIFICATION QUERIES
-- ========================================

-- Check PR count and metrics
SELECT
    '✅ SUCCESS!' as status,
    COUNT(*) as total_prs,
    COUNT(DISTINCT MODEL_USED) as unique_models,
    ROUND(AVG(EXECUTION_TIME_MS), 0) as avg_execution_time_ms
FROM PR_GENERATIONS;

-- Check new vs updates
SELECT
    CASE WHEN IS_NEW_FEATURE THEN 'New Features' ELSE 'Updates' END as type,
    COUNT(*) as count
FROM PR_GENERATIONS
GROUP BY IS_NEW_FEATURE;

-- Check model distribution
SELECT
    MODEL_USED,
    COUNT(*) as pr_count,
    ROUND(AVG(EXECUTION_TIME_MS), 0) as avg_time_ms
FROM PR_GENERATIONS
GROUP BY MODEL_USED
ORDER BY pr_count DESC;

-- View all PRs (what dashboard will show)
SELECT
    FEATURE_REQUEST,
    PR_TITLE,
    MODEL_USED,
    EXECUTION_TIME_MS,
    IS_NEW_FEATURE,
    GENERATED_AT
FROM PR_GENERATIONS
ORDER BY GENERATED_AT DESC;

-- ========================================
-- DONE!
-- ========================================
SELECT
    '✅ Perfect demo data loaded!' as message,
    '6 PRs created for postman-api-toolkit' as prs,
    'Dashboard RUN DEMO button ready!' as status,
    'Note: COMMITS table skipped - Cortex Search disabled' as note;
