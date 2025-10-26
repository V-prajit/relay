-- ========================================
-- Fix COMMITS Table Creation
-- ========================================
-- Run this in Snowflake Snowsight if COMMITS table creation failed
-- Database: BUGREWIND
-- Schema: GIT_ANALYSIS

USE DATABASE BUGREWIND;
USE SCHEMA GIT_ANALYSIS;
USE WAREHOUSE BUGREWIND_WH;

-- Drop COMMITS table if it exists (in case of partial creation)
DROP TABLE IF EXISTS COMMITS;

-- Create COMMITS table
CREATE TABLE COMMITS (
    -- Primary Key
    ID NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Commit Details
    COMMIT_HASH VARCHAR(40) NOT NULL UNIQUE,
    MESSAGE TEXT NOT NULL,
    AUTHOR VARCHAR(255) NOT NULL,
    TIMESTAMP TIMESTAMP_LTZ NOT NULL,

    -- Repository
    REPO_NAME VARCHAR(255),

    -- Diff Stats
    INSERTIONS NUMBER DEFAULT 0,
    DELETIONS NUMBER DEFAULT 0,
    FILES_CHANGED NUMBER DEFAULT 0,

    -- Files Affected (JSON array as TEXT)
    FILES_AFFECTED VARIANT
);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE COMMITS TO ROLE ACCOUNTADMIN;

-- Verify table created
SELECT 'COMMITS table created successfully' as status;
SELECT * FROM COMMITS LIMIT 1;
