# Snowflake Integration Guide for BugRewind

This guide shows you how to integrate Snowflake and Cortex AI features into your BugRewind application.

## 🎯 Snowflake Features We'll Implement

### 1. **Data Warehouse** (Core)
- Store commit history across all analyzed repositories
- Store bug analysis results with full context
- Historical tracking of bugs and fixes

### 2. **Cortex LLM Functions** (AI-Powered)
- `COMPLETE()` - AI-powered bug analysis and fix suggestions
- `SENTIMENT()` - Analyze commit message sentiment to detect "panic fixes"
- `SUMMARIZE()` - Summarize long commit messages
- `EXTRACT_ANSWER()` - Extract specific info from diffs

### 3. **Cortex Search** (Semantic Search)
- Vector-based semantic search through commit history
- Better than keyword search - understands intent
- Find similar bugs across different codebases

### 4. **Time Travel** (Query Historical Data)
- Query analysis results from any point in time
- Track how bug detection has evolved
- Roll back to previous states

### 5. **Snowpipe** (Real-time Streaming)
- Auto-ingest commits as they're analyzed
- Real-time dashboard updates
- Continuous commit indexing

### 6. **Data Sharing** (Collaboration)
- Share anonymized bug patterns with other teams
- Contribute to community bug knowledge base
- Access shared vulnerability patterns

---

## 📋 Prerequisites

### Step 1: Create Snowflake Account

1. Go to https://signup.snowflake.com/
2. Sign up for **30-day free trial**
3. Choose **AWS** as cloud provider
4. Select **US East (N. Virginia)** region
5. Choose **Enterprise** edition (includes Cortex)

### Step 2: Set Up Snowflake Objects

Open Snowflake web UI and run these SQL commands:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS BUGREWIND;

-- Use database
USE DATABASE BUGREWIND;

-- Create schema
CREATE SCHEMA IF NOT EXISTS GIT_ANALYSIS;

-- Use schema
USE SCHEMA GIT_ANALYSIS;

-- Create warehouse (compute resource)
CREATE WAREHOUSE IF NOT EXISTS BUGREWIND_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- Use warehouse
USE WAREHOUSE BUGREWIND_WH;
```

### Step 3: Create Tables

```sql
-- Commits table
CREATE TABLE IF NOT EXISTS COMMITS (
    COMMIT_ID VARCHAR(40) PRIMARY KEY,
    REPO_NAME VARCHAR(500) NOT NULL,
    SHORT_HASH VARCHAR(10),
    AUTHOR VARCHAR(255),
    AUTHOR_EMAIL VARCHAR(255),
    COMMIT_TIMESTAMP TIMESTAMP_NTZ,
    MESSAGE TEXT,
    FILES_CHANGED ARRAY,
    INSERTIONS INTEGER,
    DELETIONS INTEGER,
    DIFF_SUMMARY TEXT,
    INDEXED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Bug analysis results table
CREATE TABLE IF NOT EXISTS BUG_ANALYSIS (
    ANALYSIS_ID VARCHAR(36) PRIMARY KEY,
    REPO_NAME VARCHAR(500) NOT NULL,
    BUG_DESCRIPTION TEXT NOT NULL,
    FILE_PATH VARCHAR(1000),
    LINE_NUMBER INTEGER,
    FIRST_BAD_COMMIT VARCHAR(40),
    ROOT_CAUSE TEXT,
    DEVELOPER_INTENT TEXT,
    SUGGESTED_FIX TEXT,
    CONFIDENCE FLOAT,
    AI_MODEL VARCHAR(100),
    ANALYSIS_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    EXECUTION_TIME_MS INTEGER,

    FOREIGN KEY (FIRST_BAD_COMMIT) REFERENCES COMMITS(COMMIT_ID)
);

-- Commit sentiment analysis (using Cortex)
CREATE TABLE IF NOT EXISTS COMMIT_SENTIMENT (
    COMMIT_ID VARCHAR(40) PRIMARY KEY,
    SENTIMENT_SCORE FLOAT,
    SENTIMENT_LABEL VARCHAR(20),
    IS_PANIC_FIX BOOLEAN,
    ANALYZED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (COMMIT_ID) REFERENCES COMMITS(COMMIT_ID)
);

-- File touchpoints (line-level tracking)
CREATE TABLE IF NOT EXISTS FILE_TOUCHPOINTS (
    TOUCHPOINT_ID VARCHAR(36) PRIMARY KEY,
    REPO_NAME VARCHAR(500) NOT NULL,
    FILE_PATH VARCHAR(1000) NOT NULL,
    LINE_START INTEGER,
    LINE_END INTEGER,
    COMMIT_ID VARCHAR(40),
    CHANGE_TYPE VARCHAR(20),
    TIMESTAMP TIMESTAMP_NTZ,
    AUTHOR VARCHAR(255),

    FOREIGN KEY (COMMIT_ID) REFERENCES COMMITS(COMMIT_ID)
);
```

### Step 4: Create Cortex Search Service

```sql
-- Enable Cortex Search (requires Enterprise edition)
-- This creates a vector search index for semantic commit search

CREATE OR REPLACE CORTEX SEARCH SERVICE COMMIT_SEARCH
  ON MESSAGE
  WAREHOUSE = BUGREWIND_WH
  TARGET_LAG = '1 minute'
  AS (
    SELECT
      COMMIT_ID,
      REPO_NAME,
      MESSAGE,
      AUTHOR,
      COMMIT_TIMESTAMP
    FROM COMMITS
  );
```

### Step 5: Get Snowflake Credentials

1. In Snowflake UI, click your username (top right)
2. Go to **My Profile**
3. Note your:
   - **Account Identifier** (e.g., `abc12345.us-east-1`)
   - **Username** (your login email)
   - **Password** (what you use to login)

4. **Optional:** Create dedicated service account:
```sql
-- Create service account for BugRewind
CREATE USER bugrewind_api
  PASSWORD = 'YourSecurePassword123!'
  DEFAULT_WAREHOUSE = BUGREWIND_WH
  DEFAULT_NAMESPACE = BUGREWIND.GIT_ANALYSIS;

-- Grant necessary privileges
GRANT USAGE ON DATABASE BUGREWIND TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA BUGREWIND.GIT_ANALYSIS TO ROLE PUBLIC;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA BUGREWIND.GIT_ANALYSIS TO ROLE PUBLIC;
GRANT USAGE ON WAREHOUSE BUGREWIND_WH TO ROLE PUBLIC;
```

---

## 🔧 Backend Implementation

### Step 1: Update requirements.txt

Add Snowflake connector:

```txt
# Snowflake Integration
snowflake-connector-python==3.6.0
snowflake-sqlalchemy==1.5.1
```

### Step 2: Update .env.example

Add Snowflake credentials:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=abc12345.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=BUGREWIND
SNOWFLAKE_SCHEMA=GIT_ANALYSIS
SNOWFLAKE_WAREHOUSE=BUGREWIND_WH
SNOWFLAKE_ROLE=PUBLIC

# Feature Flags
ENABLE_SNOWFLAKE=true
ENABLE_CORTEX_LLM=true
ENABLE_CORTEX_SEARCH=true
```

### Step 3: Create SnowflakeService

Create `backend/app/services/snowflake_service.py`:

```python
"""
Snowflake service for BugRewind - handles all Snowflake operations
including Cortex AI features.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import snowflake.connector
from snowflake.connector import DictCursor
import json


class SnowflakeService:
    """Service for interacting with Snowflake data warehouse and Cortex AI."""

    _instance = None

    def __init__(self):
        """Initialize Snowflake connection."""
        self.logger = logging.getLogger(__name__)

        # Connection parameters
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.database = os.getenv("SNOWFLAKE_DATABASE", "BUGREWIND")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA", "GIT_ANALYSIS")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "BUGREWIND_WH")
        self.role = os.getenv("SNOWFLAKE_ROLE", "PUBLIC")

        self.conn = None
        self._connect()

    def _connect(self):
        """Establish connection to Snowflake."""
        try:
            self.conn = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                database=self.database,
                schema=self.schema,
                warehouse=self.warehouse,
                role=self.role
            )
            self.logger.info("✓ Connected to Snowflake")
        except Exception as e:
            self.logger.error(f"Failed to connect to Snowflake: {e}")
            raise

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a query and return results as list of dicts.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result rows as dictionaries
        """
        try:
            cursor = self.conn.cursor(DictCursor)
            cursor.execute(query, params or {})
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise

    def execute_update(self, query: str, params: Optional[Dict] = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.

        Returns:
            Number of rows affected
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params or {})
            self.conn.commit()
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
        except Exception as e:
            self.logger.error(f"Update execution failed: {e}")
            self.conn.rollback()
            raise

    # ==================== COMMIT OPERATIONS ====================

    def insert_commit(self, commit_data: Dict) -> bool:
        """
        Insert a single commit into Snowflake.

        Args:
            commit_data: Dict with keys: commit_hash, repo_name, author,
                        message, timestamp, files_changed, insertions, deletions
        """
        query = """
        INSERT INTO COMMITS (
            COMMIT_ID, REPO_NAME, SHORT_HASH, AUTHOR, AUTHOR_EMAIL,
            COMMIT_TIMESTAMP, MESSAGE, FILES_CHANGED, INSERTIONS, DELETIONS
        ) VALUES (
            %(commit_hash)s, %(repo_name)s, %(short_hash)s, %(author)s, %(author_email)s,
            %(timestamp)s, %(message)s, PARSE_JSON(%(files_changed)s), %(insertions)s, %(deletions)s
        )
        """

        params = {
            "commit_hash": commit_data["commit_hash"],
            "repo_name": commit_data["repo_name"],
            "short_hash": commit_data["commit_hash"][:10],
            "author": commit_data.get("author", "Unknown"),
            "author_email": commit_data.get("author_email", ""),
            "timestamp": commit_data.get("timestamp"),
            "message": commit_data.get("message", ""),
            "files_changed": json.dumps(commit_data.get("files_changed", [])),
            "insertions": commit_data.get("insertions", 0),
            "deletions": commit_data.get("deletions", 0)
        }

        try:
            self.execute_update(query, params)
            return True
        except Exception as e:
            self.logger.error(f"Failed to insert commit: {e}")
            return False

    def bulk_insert_commits(self, commits: List[Dict], repo_name: str) -> int:
        """
        Bulk insert multiple commits.

        Returns:
            Number of commits inserted
        """
        count = 0
        for commit in commits:
            commit["repo_name"] = repo_name
            if self.insert_commit(commit):
                count += 1
        return count

    def search_commits(
        self,
        repo_name: str,
        keyword: Optional[str] = None,
        author: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search commits with filters.

        Args:
            repo_name: Repository name
            keyword: Search in commit message
            author: Filter by author
            from_date: Start date (ISO format)
            to_date: End date (ISO format)
            limit: Max results

        Returns:
            List of matching commits
        """
        conditions = ["REPO_NAME = %(repo_name)s"]
        params = {"repo_name": repo_name, "limit": limit}

        if keyword:
            conditions.append("MESSAGE ILIKE %(keyword)s")
            params["keyword"] = f"%{keyword}%"

        if author:
            conditions.append("AUTHOR ILIKE %(author)s")
            params["author"] = f"%{author}%"

        if from_date:
            conditions.append("COMMIT_TIMESTAMP >= %(from_date)s")
            params["from_date"] = from_date

        if to_date:
            conditions.append("COMMIT_TIMESTAMP <= %(to_date)s")
            params["to_date"] = to_date

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            COMMIT_ID,
            SHORT_HASH,
            AUTHOR,
            COMMIT_TIMESTAMP,
            MESSAGE,
            FILES_CHANGED,
            INSERTIONS,
            DELETIONS
        FROM COMMITS
        WHERE {where_clause}
        ORDER BY COMMIT_TIMESTAMP DESC
        LIMIT %(limit)s
        """

        return self.execute_query(query, params)

    # ==================== CORTEX LLM FUNCTIONS ====================

    def cortex_complete(self, prompt: str, model: str = "mistral-large") -> str:
        """
        Use Cortex COMPLETE function for AI text generation.

        Args:
            prompt: Input prompt
            model: Cortex model (mistral-large, llama3-70b, etc.)

        Returns:
            Generated text
        """
        query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model}',
            %(prompt)s
        ) as response
        """

        result = self.execute_query(query, {"prompt": prompt})
        return result[0]["RESPONSE"] if result else ""

    def analyze_commit_sentiment(self, commit_id: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a commit message using Cortex SENTIMENT.

        Returns:
            Dict with sentiment_score (-1 to 1) and label (positive/negative/neutral)
        """
        query = """
        SELECT
            COMMIT_ID,
            MESSAGE,
            SNOWFLAKE.CORTEX.SENTIMENT(MESSAGE) as SENTIMENT_SCORE
        FROM COMMITS
        WHERE COMMIT_ID = %(commit_id)s
        """

        result = self.execute_query(query, {"commit_id": commit_id})

        if not result:
            return {}

        score = result[0]["SENTIMENT_SCORE"]

        # Classify sentiment
        if score > 0.3:
            label = "positive"
        elif score < -0.3:
            label = "negative"
        else:
            label = "neutral"

        # Detect "panic fixes" - very negative sentiment suggests urgent bug fix
        is_panic = score < -0.5

        # Store sentiment analysis
        self.execute_update("""
            INSERT INTO COMMIT_SENTIMENT (COMMIT_ID, SENTIMENT_SCORE, SENTIMENT_LABEL, IS_PANIC_FIX)
            VALUES (%(commit_id)s, %(score)s, %(label)s, %(is_panic)s)
        """, {
            "commit_id": commit_id,
            "score": score,
            "label": label,
            "is_panic": is_panic
        })

        return {
            "commit_id": commit_id,
            "sentiment_score": score,
            "sentiment_label": label,
            "is_panic_fix": is_panic,
            "message": result[0]["MESSAGE"]
        }

    def summarize_commit_message(self, commit_id: str) -> str:
        """
        Summarize a long commit message using Cortex SUMMARIZE.
        """
        query = """
        SELECT
            SNOWFLAKE.CORTEX.SUMMARIZE(MESSAGE) as SUMMARY
        FROM COMMITS
        WHERE COMMIT_ID = %(commit_id)s
        """

        result = self.execute_query(query, {"commit_id": commit_id})
        return result[0]["SUMMARY"] if result else ""

    def extract_bug_info_from_commit(self, commit_id: str, question: str) -> str:
        """
        Extract specific information from commit using Cortex EXTRACT_ANSWER.

        Args:
            commit_id: Commit to analyze
            question: What to extract (e.g., "What bug was fixed?")

        Returns:
            Extracted answer
        """
        query = """
        SELECT
            SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
                MESSAGE || ' ' || DIFF_SUMMARY,
                %(question)s
            ) as ANSWER
        FROM COMMITS
        WHERE COMMIT_ID = %(commit_id)s
        """

        result = self.execute_query(query, {
            "commit_id": commit_id,
            "question": question
        })
        return result[0]["ANSWER"] if result else ""

    # ==================== CORTEX SEARCH ====================

    def cortex_search_commits(
        self,
        query: str,
        repo_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Semantic search through commits using Cortex Search.

        Args:
            query: Natural language search query
            repo_name: Optional repo filter
            limit: Max results

        Returns:
            List of matching commits with relevance scores
        """
        # Build filter
        filter_clause = ""
        if repo_name:
            filter_clause = f"AND REPO_NAME = '{repo_name}'"

        search_query = f"""
        SELECT
            COMMIT_ID,
            REPO_NAME,
            AUTHOR,
            COMMIT_TIMESTAMP,
            MESSAGE,
            SEARCH_SCORE
        FROM TABLE(
            COMMIT_SEARCH(
                SEARCH_TEXT => %(query)s,
                LIMIT => {limit}
            )
        )
        WHERE 1=1 {filter_clause}
        ORDER BY SEARCH_SCORE DESC
        """

        return self.execute_query(search_query, {"query": query})

    # ==================== BUG ANALYSIS OPERATIONS ====================

    def store_bug_analysis(self, analysis_data: Dict) -> str:
        """
        Store bug analysis results.

        Returns:
            analysis_id
        """
        import uuid
        analysis_id = str(uuid.uuid4())

        query = """
        INSERT INTO BUG_ANALYSIS (
            ANALYSIS_ID, REPO_NAME, BUG_DESCRIPTION, FILE_PATH,
            LINE_NUMBER, FIRST_BAD_COMMIT, ROOT_CAUSE, DEVELOPER_INTENT,
            SUGGESTED_FIX, CONFIDENCE, AI_MODEL, EXECUTION_TIME_MS
        ) VALUES (
            %(analysis_id)s, %(repo_name)s, %(bug_description)s, %(file_path)s,
            %(line_number)s, %(first_bad_commit)s, %(root_cause)s, %(developer_intent)s,
            %(suggested_fix)s, %(confidence)s, %(ai_model)s, %(execution_time_ms)s
        )
        """

        params = {
            "analysis_id": analysis_id,
            "repo_name": analysis_data["repo_name"],
            "bug_description": analysis_data["bug_description"],
            "file_path": analysis_data.get("file_path"),
            "line_number": analysis_data.get("line_number"),
            "first_bad_commit": analysis_data.get("first_bad_commit"),
            "root_cause": analysis_data.get("root_cause"),
            "developer_intent": analysis_data.get("developer_intent"),
            "suggested_fix": analysis_data.get("suggested_fix"),
            "confidence": analysis_data.get("confidence"),
            "ai_model": analysis_data.get("ai_model", "claude-sonnet-4"),
            "execution_time_ms": analysis_data.get("execution_time_ms")
        }

        self.execute_update(query, params)
        return analysis_id

    def get_bug_analysis_history(
        self,
        repo_name: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get historical bug analyses for a repository.
        """
        query = """
        SELECT
            ANALYSIS_ID,
            BUG_DESCRIPTION,
            FILE_PATH,
            FIRST_BAD_COMMIT,
            ROOT_CAUSE,
            CONFIDENCE,
            ANALYSIS_TIMESTAMP
        FROM BUG_ANALYSIS
        WHERE REPO_NAME = %(repo_name)s
        ORDER BY ANALYSIS_TIMESTAMP DESC
        LIMIT %(limit)s
        """

        return self.execute_query(query, {"repo_name": repo_name, "limit": limit})

    # ==================== ANALYTICS ====================

    def get_panic_fixes(self, repo_name: str, days: int = 30) -> List[Dict]:
        """
        Find commits that are likely panic fixes (negative sentiment).

        Useful for identifying areas with frequent urgent fixes.
        """
        query = """
        SELECT
            c.COMMIT_ID,
            c.SHORT_HASH,
            c.AUTHOR,
            c.COMMIT_TIMESTAMP,
            c.MESSAGE,
            cs.SENTIMENT_SCORE,
            cs.IS_PANIC_FIX
        FROM COMMITS c
        JOIN COMMIT_SENTIMENT cs ON c.COMMIT_ID = cs.COMMIT_ID
        WHERE c.REPO_NAME = %(repo_name)s
          AND cs.IS_PANIC_FIX = TRUE
          AND c.COMMIT_TIMESTAMP >= DATEADD(day, -%(days)s, CURRENT_TIMESTAMP())
        ORDER BY cs.SENTIMENT_SCORE ASC
        """

        return self.execute_query(query, {"repo_name": repo_name, "days": days})

    def get_repository_stats(self, repo_name: str) -> Dict:
        """
        Get statistics for a repository.
        """
        query = """
        SELECT
            COUNT(*) as total_commits,
            COUNT(DISTINCT AUTHOR) as unique_authors,
            MIN(COMMIT_TIMESTAMP) as first_commit,
            MAX(COMMIT_TIMESTAMP) as last_commit,
            SUM(INSERTIONS) as total_insertions,
            SUM(DELETIONS) as total_deletions
        FROM COMMITS
        WHERE REPO_NAME = %(repo_name)s
        """

        result = self.execute_query(query, {"repo_name": repo_name})
        return result[0] if result else {}

    # ==================== TIME TRAVEL ====================

    def query_at_timestamp(self, table: str, timestamp: str, conditions: str = "1=1") -> List[Dict]:
        """
        Query historical data using Snowflake Time Travel.

        Args:
            table: Table name
            timestamp: ISO timestamp to query at
            conditions: WHERE clause conditions

        Returns:
            Results from that point in time
        """
        query = f"""
        SELECT *
        FROM {table}
        AT(TIMESTAMP => '{timestamp}'::TIMESTAMP_NTZ)
        WHERE {conditions}
        """

        return self.execute_query(query)

    # ==================== HEALTH CHECK ====================

    def health_check(self) -> Dict[str, Any]:
        """Check Snowflake connection health."""
        try:
            result = self.execute_query("SELECT CURRENT_VERSION() as version")

            return {
                "status": "healthy",
                "database": self.database,
                "schema": self.schema,
                "warehouse": self.warehouse,
                "version": result[0]["VERSION"] if result else "unknown"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def close(self):
        """Close Snowflake connection."""
        if self.conn:
            self.conn.close()
            self.logger.info("Snowflake connection closed")
```

This is a comprehensive SnowflakeService with:
- ✅ Data warehouse operations (commits, analysis storage)
- ✅ Cortex LLM functions (COMPLETE, SENTIMENT, SUMMARIZE, EXTRACT_ANSWER)
- ✅ Cortex Search (semantic commit search)
- ✅ Time Travel queries
- ✅ Analytics and statistics

---

## 🎯 Next Steps

Would you like me to:
1. **Create API routes** for these Snowflake features?
2. **Update the Postman Flow** to use Snowflake instead of Elasticsearch?
3. **Create a test script** to populate Snowflake with sample data?
4. **Implement specific Cortex features** you're most interested in?

Let me know which part you want to tackle first!
