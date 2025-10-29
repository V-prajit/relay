"""
Snowflake service for BugRewind - handles all Snowflake operations
including Cortex AI features.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class SnowflakeService:
    """Service for interacting with Snowflake data warehouse and Cortex AI."""

    _instance = None

    def __init__(self):
        """Initialize Snowflake connection."""
        self.logger = logging.getLogger(__name__)

        # Check if Snowflake is enabled
        if os.getenv("ENABLE_SNOWFLAKE", "false").lower() != "true":
            self.logger.warning("Snowflake is disabled. Set ENABLE_SNOWFLAKE=true to enable.")
            self.conn = None
            return

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
            import snowflake.connector

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
        except ImportError:
            self.logger.error("snowflake-connector-python not installed. Run: pip install snowflake-connector-python")
            self.conn = None
        except Exception as e:
            self.logger.error(f"Failed to connect to Snowflake: {e}")
            self.conn = None

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def is_connected(self) -> bool:
        """Check if Snowflake is connected."""
        return self.conn is not None

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a query and return results as list of dicts.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result rows as dictionaries
        """
        if not self.is_connected():
            self.logger.error("Snowflake not connected")
            return []

        try:
            from snowflake.connector import DictCursor

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
        if not self.is_connected():
            self.logger.error("Snowflake not connected")
            return 0

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
        if not self.is_connected():
            return False

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
        if not self.is_connected():
            return []

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

    def cortex_complete(self, prompt: str, model: str = "llama3.1-8b") -> str:
        """
        Use Cortex COMPLETE function for AI text generation.

        Updated: Using llama3.1-8b for 3x faster inference.

        Args:
            prompt: Input prompt
            model: Cortex model (mistral-large, llama3-70b, mixtral-8x7b, etc.)

        Returns:
            Generated text
        """
        if not self.is_connected():
            return ""

        if os.getenv("ENABLE_CORTEX_LLM", "false").lower() != "true":
            self.logger.warning("Cortex LLM is disabled")
            return ""

        query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model}',
            %(prompt)s
        ) as response
        """

        try:
            result = self.execute_query(query, {"prompt": prompt})
            return result[0]["RESPONSE"] if result else ""
        except Exception as e:
            self.logger.error(f"Cortex COMPLETE failed: {e}")
            return ""

    def analyze_commit_sentiment(self, commit_id: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a commit message using Cortex SENTIMENT.

        Returns:
            Dict with sentiment_score (-1 to 1) and label (positive/negative/neutral)
        """
        if not self.is_connected():
            return {}

        if os.getenv("ENABLE_CORTEX_LLM", "false").lower() != "true":
            self.logger.warning("Cortex LLM is disabled")
            return {}

        query = """
        SELECT
            COMMIT_ID,
            MESSAGE,
            SNOWFLAKE.CORTEX.SENTIMENT(MESSAGE) as SENTIMENT_SCORE
        FROM COMMITS
        WHERE COMMIT_ID = %(commit_id)s
        """

        try:
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
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return {}

    def summarize_commit_message(self, commit_id: str) -> str:
        """
        Summarize a long commit message using Cortex SUMMARIZE.
        """
        if not self.is_connected():
            return ""

        if os.getenv("ENABLE_CORTEX_LLM", "false").lower() != "true":
            return ""

        query = """
        SELECT
            SNOWFLAKE.CORTEX.SUMMARIZE(MESSAGE) as SUMMARY
        FROM COMMITS
        WHERE COMMIT_ID = %(commit_id)s
        """

        try:
            result = self.execute_query(query, {"commit_id": commit_id})
            return result[0]["SUMMARY"] if result else ""
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            return ""

    def extract_bug_info_from_commit(self, commit_id: str, question: str) -> str:
        """
        Extract specific information from commit using Cortex EXTRACT_ANSWER.

        Args:
            commit_id: Commit to analyze
            question: What to extract (e.g., "What bug was fixed?")

        Returns:
            Extracted answer
        """
        if not self.is_connected():
            return ""

        if os.getenv("ENABLE_CORTEX_LLM", "false").lower() != "true":
            return ""

        query = """
        SELECT
            SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
                MESSAGE || ' ' || COALESCE(DIFF_SUMMARY, ''),
                %(question)s
            ) as ANSWER
        FROM COMMITS
        WHERE COMMIT_ID = %(commit_id)s
        """

        try:
            result = self.execute_query(query, {
                "commit_id": commit_id,
                "question": question
            })
            return result[0]["ANSWER"] if result else ""
        except Exception as e:
            self.logger.error(f"Extract answer failed: {e}")
            return ""

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
        if not self.is_connected():
            return []

        if os.getenv("ENABLE_CORTEX_SEARCH", "false").lower() != "true":
            self.logger.warning("Cortex Search is disabled")
            return []

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

        try:
            return self.execute_query(search_query, {"query": query})
        except Exception as e:
            self.logger.error(f"Cortex search failed: {e}")
            return []

    # ==================== PR GENERATION (CORTEX AI) ====================

    def generate_pr_with_cortex(
        self,
        feature_request: str,
        impacted_files: List[str],
        is_new_feature: bool,
        repo_name: str,
        conflict_info: Optional[str] = None,
        model: str = "llama3.1-8b"
    ) -> Dict[str, Any]:
        """
        Generate PR content using Snowflake Cortex LLM.

        This is the HYBRID AI approach:
        - Postman AI Agent orchestrates (decides when to call this)
        - Snowflake Cortex generates (decides what code to write)

        Args:
            feature_request: Natural language feature description
            impacted_files: List of files from Ripgrep search
            is_new_feature: Whether no existing files found
            repo_name: Repository name
            conflict_info: Optional conflict warning
            model: Cortex model to use

        Returns:
            Dict with pr_title, pr_description, branch_name, generated_by
        """
        if not self.is_connected():
            raise Exception("Snowflake not connected")

        if os.getenv("ENABLE_CORTEX_LLM", "false").lower() != "true":
            raise Exception("Cortex LLM is disabled. Set ENABLE_CORTEX_LLM=true")

        import uuid
        from datetime import datetime

        # Build prompt for Cortex
        files_str = "\n".join([f"- {f}" for f in impacted_files]) if impacted_files else "No existing files"
        conflict_str = f"\n\n⚠️ CONFLICTS DETECTED:\n{conflict_info}" if conflict_info else ""

        prompt = f"""You are a senior software engineer generating PR content.

Feature Request: {feature_request}

Repository: {repo_name}

Files to Modify:
{files_str}

Is New Feature: {"Yes - create new files" if is_new_feature else "No - modify existing files"}
{conflict_str}

Generate a professional PR with:
1. Title (concise, starts with "feat:" or "fix:")
2. Description (markdown formatted, includes acceptance criteria)
3. If existing files: suggest specific code changes
4. If new feature: suggest file structure and key functions

Keep PR scope small (≤30 lines of changes recommended).

Return response in this format:
TITLE: [your title here]

DESCRIPTION:
[your markdown description here]

CHANGES:
[specific code changes or new file suggestions]

ACCEPTANCE_CRITERIA:
- [criterion 1]
- [criterion 2]
- [criterion 3]
"""

        try:
            # Call Cortex COMPLETE
            start_time = datetime.now()
            result = self.execute_query(f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    %(model)s,
                    %(prompt)s
                ) as response
            """, {
                "model": model,
                "prompt": prompt
            })
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            if not result or not result[0].get("RESPONSE"):
                raise Exception("Cortex returned empty response")

            cortex_response = result[0]["RESPONSE"]

            # Parse response
            pr_title = self._extract_section(cortex_response, "TITLE:", "\n")
            pr_description = self._extract_section(cortex_response, "DESCRIPTION:", "CHANGES:")
            code_changes = self._extract_section(cortex_response, "CHANGES:", "ACCEPTANCE_CRITERIA:")
            acceptance_criteria = self._extract_section(cortex_response, "ACCEPTANCE_CRITERIA:", None)

            # Generate unique branch name
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            guid = str(uuid.uuid4())[:8]
            feature_slug = feature_request[:30].lower().replace(" ", "-").replace("/", "-")
            branch_name = f"pm-copilot/{feature_slug}-{timestamp}-{guid}"

            # Combine description with code changes
            full_description = f"""{pr_description}

## Proposed Changes

{code_changes}

## Acceptance Criteria

{acceptance_criteria}

---
🤖 Generated by **Postman AI Agent** (orchestration) + **Snowflake Cortex** ({model})
⚡ Powered by Hybrid AI Architecture
"""

            # Store execution data in Snowflake
            try:
                self.execute_update("""
                    INSERT INTO PR_GENERATIONS (
                        GENERATION_ID, REPO_NAME, FEATURE_REQUEST, IMPACTED_FILES,
                        IS_NEW_FEATURE, PR_TITLE, BRANCH_NAME, GENERATED_BY_MODEL,
                        EXECUTION_TIME_MS, GENERATED_AT
                    ) VALUES (
                        %(gen_id)s, %(repo_name)s, %(feature)s, PARSE_JSON(%(files)s),
                        %(is_new)s, %(title)s, %(branch)s, %(model)s,
                        %(exec_time)s, CURRENT_TIMESTAMP()
                    )
                """, {
                    "gen_id": str(uuid.uuid4()),
                    "repo_name": repo_name,
                    "feature": feature_request,
                    "files": json.dumps(impacted_files),
                    "is_new": is_new_feature,
                    "title": pr_title,
                    "branch": branch_name,
                    "model": f"cortex-{model}",
                    "exec_time": execution_time_ms
                })
            except Exception as e:
                self.logger.warning(f"Failed to store PR generation data: {e}")

            return {
                "pr_title": pr_title.strip(),
                "pr_description": full_description.strip(),
                "branch_name": branch_name,
                "generated_by": f"Snowflake Cortex ({model})",
                "execution_time_ms": execution_time_ms,
                "model": model
            }

        except Exception as e:
            self.logger.error(f"Cortex PR generation failed: {e}")
            raise Exception(f"Failed to generate PR with Cortex: {str(e)}")

    def _extract_section(self, text: str, start_marker: str, end_marker: Optional[str]) -> str:
        """Extract section between markers from Cortex response."""
        try:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return ""

            start_idx += len(start_marker)

            if end_marker:
                end_idx = text.find(end_marker, start_idx)
                if end_idx == -1:
                    return text[start_idx:].strip()
                return text[start_idx:end_idx].strip()
            else:
                return text[start_idx:].strip()
        except Exception:
            return ""

    # ==================== BUG ANALYSIS OPERATIONS ====================

    def store_bug_analysis(self, analysis_data: Dict) -> str:
        """
        Store bug analysis results.

        Returns:
            analysis_id
        """
        if not self.is_connected():
            return ""

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

        try:
            self.execute_update(query, params)
            return analysis_id
        except Exception as e:
            self.logger.error(f"Failed to store analysis: {e}")
            return ""

    def get_bug_analysis_history(
        self,
        repo_name: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get historical bug analyses for a repository.
        """
        if not self.is_connected():
            return []

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
        if not self.is_connected():
            return []

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
        if not self.is_connected():
            return {}

        query = """
        SELECT
            COUNT(*) as TOTAL_COMMITS,
            COUNT(DISTINCT AUTHOR) as UNIQUE_AUTHORS,
            MIN(COMMIT_TIMESTAMP) as FIRST_COMMIT,
            MAX(COMMIT_TIMESTAMP) as LAST_COMMIT,
            SUM(INSERTIONS) as TOTAL_INSERTIONS,
            SUM(DELETIONS) as TOTAL_DELETIONS
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
        if not self.is_connected():
            return []

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
        if not self.is_connected():
            return {
                "status": "disabled",
                "message": "Snowflake is not enabled or not connected"
            }

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
