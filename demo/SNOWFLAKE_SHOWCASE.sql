-- ========================================
-- SNOWFLAKE CORTEX SHOWCASE FOR DEMO
-- ========================================
-- Run these queries during the 3-minute demo to show Snowflake capabilities

USE DATABASE BUGREWIND;
USE SCHEMA GIT_ANALYSIS;
USE WAREHOUSE BUGREWIND_WH;

-- ==================== DEMO QUERY 1 ====================
-- Show PR generations stored in Snowflake
-- This proves that all data from Postman Flow is stored

SELECT
    FEATURE_REQUEST,
    PR_TITLE,
    GENERATED_BY_MODEL,
    EXECUTION_TIME_MS,
    GENERATED_AT,
    ARRAY_SIZE(IMPACTED_FILES) as files_count
FROM PR_GENERATIONS
ORDER BY GENERATED_AT DESC
LIMIT 5;

-- Expected output: Show recent PR generations with execution times


-- ==================== DEMO QUERY 2 ====================
-- LIVE Cortex LLM generation (run this during demo!)
-- This shows Snowflake Cortex generating PR content in real-time

SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mistral-large',
    'You are a senior engineer. Write a PR title for: Fix mobile login responsive design on small screens'
) as cortex_live_generation;

-- Expected output: "fix: Improve mobile login responsive layout"


-- ==================== DEMO QUERY 3 ====================
-- Cortex Sentiment Analysis on commit messages
-- Shows Cortex AI analyzing developer mood/urgency

SELECT
    'Fixed critical login bug ASAP!!!' as commit_message,
    SNOWFLAKE.CORTEX.SENTIMENT('Fixed critical login bug ASAP!!!') as sentiment_score,
    CASE
        WHEN SNOWFLAKE.CORTEX.SENTIMENT('Fixed critical login bug ASAP!!!') < -0.5 THEN 'PANIC FIX 🚨'
        WHEN SNOWFLAKE.CORTEX.SENTIMENT('Fixed critical login bug ASAP!!!') < 0 THEN 'Urgent fix'
        ELSE 'Normal commit'
    END as fix_urgency
UNION ALL
SELECT
    'Added new feature: OAuth login' as commit_message,
    SNOWFLAKE.CORTEX.SENTIMENT('Added new feature: OAuth login') as sentiment_score,
    CASE
        WHEN SNOWFLAKE.CORTEX.SENTIMENT('Added new feature: OAuth login') < -0.5 THEN 'PANIC FIX 🚨'
        WHEN SNOWFLAKE.CORTEX.SENTIMENT('Added new feature: OAuth login') < 0 THEN 'Urgent fix'
        ELSE 'Normal commit'
    END as fix_urgency;

-- Expected output: First is panic fix (-0.8), second is normal (0.4)


-- ==================== DEMO QUERY 4 ====================
-- Analytics: PR generation performance over time

SELECT
    DATE_TRUNC('day', GENERATED_AT) as generation_date,
    COUNT(*) as prs_generated,
    AVG(EXECUTION_TIME_MS) as avg_execution_ms,
    COUNT(DISTINCT GENERATED_BY_MODEL) as models_used
FROM PR_GENERATIONS
WHERE GENERATED_AT >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY generation_date
ORDER BY generation_date DESC;

-- Expected output: Daily PR generation stats


-- ==================== DEMO QUERY 5 ====================
-- Cortex Summarize - Condense long feature requests

SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
    'We need to fix the mobile login page because users on small screens are having trouble seeing the login button and the form fields are not properly aligned when the viewport width is less than 768px and also the error messages overlap with the input fields'
) as summarized_request;

-- Expected output: "Fix mobile login page responsive design for screens <768px"


-- ==================== DEMO QUERY 6 ====================
-- Time Travel - Query historical PR generations
-- Shows Snowflake's unique time travel feature

SELECT
    FEATURE_REQUEST,
    PR_TITLE,
    GENERATED_AT
FROM PR_GENERATIONS
AT(OFFSET => -60*5) -- 5 minutes ago
ORDER BY GENERATED_AT DESC
LIMIT 3;

-- Expected output: PRs as they existed 5 minutes ago


-- ==================== DEMO QUERY 7 ====================
-- Semantic Search (if Cortex Search is enabled)
-- Search for similar feature requests using natural language

-- Note: This requires COMMIT_SEARCH service to be created
-- Uncomment if you have Cortex Search enabled

/*
SELECT
    COMMIT_ID,
    MESSAGE,
    SEARCH_SCORE
FROM TABLE(
    COMMIT_SEARCH(
        SEARCH_TEXT => 'mobile responsive login issues',
        LIMIT => 5
    )
)
ORDER BY SEARCH_SCORE DESC;
*/


-- ==================== BONUS: Cost Analysis ====================
-- Show cost efficiency of using Snowflake vs external AI APIs

SELECT
    COUNT(*) as total_prs_generated,
    AVG(EXECUTION_TIME_MS) as avg_time_ms,
    SUM(EXECUTION_TIME_MS) / 1000.0 / 60.0 as total_compute_minutes,
    '~$0.001 per PR' as estimated_cost_per_pr,
    'vs $0.015 for Claude API' as comparison
FROM PR_GENERATIONS;


-- ==================== DEMO SCRIPT ====================
-- Run in this order during 3-minute demo:

-- 1. Show Query 1 → Prove data is stored
-- 2. Run Query 2 LIVE → Show Cortex generating PR title in real-time
-- 3. Show Query 3 → Demonstrate sentiment analysis
-- 4. Show Query 4 → Analytics dashboard potential
-- 5. Optional: Query 6 → Time Travel feature

-- KEY TALKING POINTS:
-- ✅ "All data stored in Snowflake data warehouse"
-- ✅ "Cortex LLM generates code without external API"
-- ✅ "Built-in AI functions: COMPLETE, SENTIMENT, SUMMARIZE"
-- ✅ "Time Travel lets us query historical data"
-- ✅ "Cost effective: ~$0.001 vs $0.015 for external AI"
