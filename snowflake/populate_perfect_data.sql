-- ========================================
-- Perfect Demo Data for Video Recording
-- ========================================
-- Run this AFTER fix_commits_table.sql
-- This populates beautiful, realistic data for the dashboard

USE DATABASE BUGREWIND;
USE SCHEMA GIT_ANALYSIS;
USE WAREHOUSE BUGREWIND_WH;

-- ========================================
-- CLEAR OLD DATA (fresh start)
-- ========================================

DELETE FROM PR_GENERATIONS;
DELETE FROM COMMITS;

-- ========================================
-- INSERT PERFECT PR DATA
-- ========================================
-- 6 PRs showcasing different features, models, and times

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
-- INSERT COMMIT DATA (for Cortex Search demo)
-- ========================================

INSERT INTO COMMITS (
    COMMIT_HASH,
    MESSAGE,
    AUTHOR,
    TIMESTAMP,
    REPO_NAME,
    INSERTIONS,
    DELETIONS,
    FILES_CHANGED,
    FILES_AFFECTED
) VALUES
    (
        'a1b2c3d4e5f6g7h8i9j0',
        'feat: Add rate limiting middleware to prevent abuse',
        'alice.chen@example.com',
        DATEADD(hour, -3, CURRENT_TIMESTAMP()),
        'V-prajit/postman-api-toolkit',
        67,
        3,
        2,
        PARSE_JSON('["middleware/rateLimiter.js", "server.js"]')
    ),
    (
        'b2c3d4e5f6g7h8i9j0k1',
        'feat: Implement JWT authentication system',
        'bob.smith@example.com',
        DATEADD(hour, -8, CURRENT_TIMESTAMP()),
        'V-prajit/postman-api-toolkit',
        145,
        8,
        4,
        PARSE_JSON('["routes/auth.js", "middleware/authenticate.js", "server.js", "package.json"]')
    ),
    (
        'c3d4e5f6g7h8i9j0k1l2',
        'fix: Add response time tracking to logger',
        'charlie.wong@example.com',
        DATEADD(hour, -12, CURRENT_TIMESTAMP()),
        'V-prajit/postman-api-toolkit',
        23,
        5,
        1,
        PARSE_JSON('["middleware/logger.js"]')
    ),
    (
        'd4e5f6g7h8i9j0k1l2m3',
        'feat: Add CORS middleware for cross-origin support',
        'diana.patel@example.com',
        DATEADD(day, -1, CURRENT_TIMESTAMP()),
        'V-prajit/postman-api-toolkit',
        34,
        0,
        2,
        PARSE_JSON('["middleware/cors.js", "server.js"]')
    ),
    (
        'e5f6g7h8i9j0k1l2m3n4',
        'feat: Add request validation with express-validator',
        'ethan.garcia@example.com',
        DATEADD(day, -2, CURRENT_TIMESTAMP()),
        'V-prajit/postman-api-toolkit',
        89,
        4,
        3,
        PARSE_JSON('["middleware/validator.js", "routes/users.js", "package.json"]')
    ),
    (
        'f6g7h8i9j0k1l2m3n4o5',
        'feat: Enhance health endpoint with system metrics',
        'fiona.lee@example.com',
        DATEADD(day, -3, CURRENT_TIMESTAMP()),
        'V-prajit/postman-api-toolkit',
        56,
        12,
        1,
        PARSE_JSON('["routes/health.js"]')
    ),
    (
        'g7h8i9j0k1l2m3n4o5p6',
        'docs: Add comprehensive API documentation',
        'george.kim@example.com',
        DATEADD(day, -4, CURRENT_TIMESTAMP()),
        'V-prajit/postman-api-toolkit',
        234,
        0,
        3,
        PARSE_JSON('["docs/API.md", "README.md", "docs/AUTHENTICATION.md"]')
    ),
    (
        'h8i9j0k1l2m3n4o5p6q7',
        'test: Add unit tests for middleware functions',
        'hannah.nguyen@example.com',
        DATEADD(day, -5, CURRENT_TIMESTAMP()),
        'V-prajit/postman-api-toolkit',
        178,
        0,
        5,
        PARSE_JSON('["tests/rateLimiter.test.js", "tests/auth.test.js", "tests/validator.test.js", "package.json", "jest.config.js"]')
    );

-- ========================================
-- VERIFICATION QUERIES
-- ========================================

-- Check PR count and metrics
SELECT
    COUNT(*) as total_prs,
    COUNT(DISTINCT MODEL_USED) as unique_models,
    ROUND(AVG(EXECUTION_TIME_MS), 0) as avg_execution_time_ms,
    MIN(GENERATED_AT) as oldest_pr,
    MAX(GENERATED_AT) as newest_pr
FROM PR_GENERATIONS;

-- Check new vs updates
SELECT
    IS_NEW_FEATURE,
    COUNT(*) as count
FROM PR_GENERATIONS
GROUP BY IS_NEW_FEATURE;

-- Check model distribution
SELECT
    MODEL_USED,
    COUNT(*) as count,
    ROUND(AVG(EXECUTION_TIME_MS), 0) as avg_time_ms
FROM PR_GENERATIONS
GROUP BY MODEL_USED
ORDER BY count DESC;

-- Check commits
SELECT
    COUNT(*) as total_commits,
    COUNT(DISTINCT AUTHOR) as unique_authors,
    SUM(INSERTIONS) as total_lines_added,
    SUM(DELETIONS) as total_lines_removed
FROM COMMITS;

-- View recent PRs (what dashboard will show)
SELECT
    FEATURE_REQUEST,
    PR_TITLE,
    MODEL_USED,
    EXECUTION_TIME_MS,
    IS_NEW_FEATURE,
    GENERATED_AT
FROM PR_GENERATIONS
ORDER BY GENERATED_AT DESC
LIMIT 6;

-- ========================================
-- SUCCESS MESSAGE
-- ========================================
SELECT '✅ Perfect demo data loaded!' as status,
       '6 PRs created for postman-api-toolkit' as pr_count,
       '8 commits added for Cortex Search' as commit_count,
       '3 AI models used (Mistral, Llama, Mixtral)' as models,
       'Dashboard ready for video demo!' as ready;
