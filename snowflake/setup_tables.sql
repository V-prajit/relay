-- ========================================
-- Snowflake Table Setup for BugRewind
-- ========================================
-- Run this in Snowflake Snowsight to create tables and sample data
-- Database: BUGREWIND
-- Schema: GIT_ANALYSIS

-- Use the correct database and schema
USE DATABASE BUGREWIND;
USE SCHEMA GIT_ANALYSIS;
USE WAREHOUSE BUGREWIND_WH;

-- ========================================
-- 1. CREATE PR_GENERATIONS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS PR_GENERATIONS (
    -- Primary Key
    ID NUMBER AUTOINCREMENT PRIMARY KEY,

    -- PR Details
    FEATURE_REQUEST TEXT NOT NULL,
    PR_TITLE TEXT NOT NULL,
    PR_DESCRIPTION TEXT,
    BRANCH_NAME TEXT NOT NULL,

    -- Classification
    IS_NEW_FEATURE BOOLEAN DEFAULT FALSE,

    -- Repository Info
    REPO_NAME TEXT,

    -- AI Model Info
    MODEL_USED TEXT DEFAULT 'mistral-large',
    EXECUTION_TIME_MS NUMBER,

    -- Metadata
    GENERATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),

    -- File Impact (optional)
    IMPACTED_FILES ARRAY,
    CONFLICT_INFO TEXT
);

-- ========================================
-- 2. CREATE COMMITS TABLE (for Cortex Search demo)
-- ========================================

CREATE TABLE IF NOT EXISTS COMMITS (
    -- Primary Key
    ID NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Commit Details
    COMMIT_HASH TEXT NOT NULL UNIQUE,
    MESSAGE TEXT NOT NULL,
    AUTHOR TEXT NOT NULL,
    TIMESTAMP TIMESTAMP_LTZ NOT NULL,

    -- Repository
    REPO_NAME TEXT,

    -- Diff Stats
    INSERTIONS NUMBER DEFAULT 0,
    DELETIONS NUMBER DEFAULT 0,
    FILES_CHANGED NUMBER DEFAULT 0,

    -- Files Affected
    FILES_AFFECTED ARRAY
);

-- ========================================
-- 3. INSERT SAMPLE DATA INTO PR_GENERATIONS
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
    (
        'fix mobile login responsive design on small screens',
        'fix: Mobile login responsive design',
        'Fixed responsive layout issues on mobile login screen. Updated CSS media queries and flexbox layout.',
        'fix/mobile-login-responsive',
        FALSE,
        'V-prajit/youareabsolutelyright',
        'mistral-large',
        2341,
        DATEADD(hour, -2, CURRENT_TIMESTAMP())
    ),
    (
        'add dark mode toggle to settings page',
        'feat: Add dark mode toggle',
        'Implemented dark mode toggle in settings. Added theme context provider and CSS variable switching.',
        'feature/dark-mode-toggle',
        TRUE,
        'V-prajit/youareabsolutelyright',
        'mistral-large',
        3120,
        DATEADD(hour, -5, CURRENT_TIMESTAMP())
    ),
    (
        'update search functionality to include fuzzy matching',
        'feat: Update search with fuzzy matching',
        'Enhanced search algorithm with fuzzy string matching. Integrated Fuse.js library for better search results.',
        'feature/fuzzy-search',
        FALSE,
        'V-prajit/youareabsolutelyright',
        'llama3-70b',
        2890,
        DATEADD(hour, -8, CURRENT_TIMESTAMP())
    ),
    (
        'fix authentication bug causing 401 errors',
        'fix: Authentication 401 errors',
        'Fixed intermittent 401 errors in token refresh logic. Updated JWT expiration handling.',
        'fix/auth-401',
        FALSE,
        'V-prajit/youareabsolutelyright',
        'mistral-large',
        1987,
        DATEADD(day, -1, CURRENT_TIMESTAMP())
    ),
    (
        'add OAuth 2.0 authentication provider',
        'feat: Add OAuth 2.0 provider',
        'Implemented OAuth 2.0 authentication flow. Added Google and GitHub OAuth providers.',
        'feature/oauth-provider',
        TRUE,
        'V-prajit/youareabsolutelyright',
        'mixtral-8x7b',
        4250,
        DATEADD(day, -2, CURRENT_TIMESTAMP())
    ),
    (
        'optimize database queries for dashboard loading',
        'perf: Optimize dashboard queries',
        'Reduced dashboard load time by 60% through query optimization and indexing.',
        'perf/dashboard-queries',
        FALSE,
        'V-prajit/youareabsolutelyright',
        'mistral-large',
        2567,
        DATEADD(day, -3, CURRENT_TIMESTAMP())
    ),
    (
        'add user profile page with avatar upload',
        'feat: User profile with avatar',
        'Created user profile page with avatar upload functionality. Integrated AWS S3 for image storage.',
        'feature/user-profile',
        TRUE,
        'V-prajit/youareabsolutelyright',
        'llama3-70b',
        3845,
        DATEADD(day, -4, CURRENT_TIMESTAMP())
    ),
    (
        'fix memory leak in websocket connections',
        'fix: WebSocket memory leak',
        'Fixed memory leak caused by unclosed WebSocket connections. Added proper cleanup on unmount.',
        'fix/websocket-leak',
        FALSE,
        'V-prajit/youareabsolutelyright',
        'mistral-large',
        2103,
        DATEADD(day, -5, CURRENT_TIMESTAMP())
    );

-- ========================================
-- 4. INSERT SAMPLE DATA INTO COMMITS
-- ========================================

INSERT INTO COMMITS (
    COMMIT_HASH,
    MESSAGE,
    AUTHOR,
    TIMESTAMP,
    REPO_NAME,
    INSERTIONS,
    DELETIONS,
    FILES_CHANGED
) VALUES
    (
        'a1b2c3d4e5f6',
        'fix: Mobile login responsive design on small screens',
        'alice@example.com',
        DATEADD(hour, -2, CURRENT_TIMESTAMP()),
        'V-prajit/youareabsolutelyright',
        45,
        12,
        3
    ),
    (
        'f6e5d4c3b2a1',
        'feat: Add dark mode toggle to settings',
        'bob@example.com',
        DATEADD(hour, -5, CURRENT_TIMESTAMP()),
        'V-prajit/youareabsolutelyright',
        128,
        8,
        7
    ),
    (
        'b2c3d4e5f6a1',
        'fix: Critical authentication bug causing 401 errors',
        'charlie@example.com',
        DATEADD(day, -1, CURRENT_TIMESTAMP()),
        'V-prajit/youareabsolutelyright',
        23,
        15,
        2
    ),
    (
        'c3d4e5f6a1b2',
        'feat: Implement OAuth 2.0 authentication',
        'alice@example.com',
        DATEADD(day, -2, CURRENT_TIMESTAMP()),
        'V-prajit/youareabsolutelyright',
        234,
        0,
        12
    ),
    (
        'd4e5f6a1b2c3',
        'perf: Optimize database queries for faster dashboard',
        'bob@example.com',
        DATEADD(day, -3, CURRENT_TIMESTAMP()),
        'V-prajit/youareabsolutelyright',
        67,
        89,
        5
    );

-- ========================================
-- 5. VERIFY DATA
-- ========================================

-- Check PR_GENERATIONS table
SELECT
    COUNT(*) as total_prs,
    COUNT(DISTINCT MODEL_USED) as models_used,
    AVG(EXECUTION_TIME_MS) as avg_execution_time,
    MIN(GENERATED_AT) as first_pr,
    MAX(GENERATED_AT) as latest_pr
FROM PR_GENERATIONS;

-- Check COMMITS table
SELECT
    COUNT(*) as total_commits,
    COUNT(DISTINCT AUTHOR) as unique_authors,
    SUM(INSERTIONS) as total_insertions,
    SUM(DELETIONS) as total_deletions
FROM COMMITS;

-- View recent PRs
SELECT
    FEATURE_REQUEST,
    PR_TITLE,
    MODEL_USED,
    EXECUTION_TIME_MS,
    GENERATED_AT
FROM PR_GENERATIONS
ORDER BY GENERATED_AT DESC
LIMIT 5;

-- ========================================
-- 6. GRANT PERMISSIONS (if needed)
-- ========================================

-- Grant access to your role (replace ACCOUNTADMIN with your role if different)
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE PR_GENERATIONS TO ROLE ACCOUNTADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE COMMITS TO ROLE ACCOUNTADMIN;

-- ========================================
-- SUCCESS!
-- ========================================
-- Tables created with sample data.
-- You can now:
-- 1. Test the RUN DEMO button (should work now)
-- 2. Upload the cortex_analyst_semantic_model.yaml
-- 3. Test natural language queries in Cortex Analyst
