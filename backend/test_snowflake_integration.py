"""
Test script for Snowflake integration

This script tests the Snowflake connection and basic operations.
Run this after setting up your Snowflake account and configuring .env
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from app.services.snowflake_service import SnowflakeService

# Load environment variables
load_dotenv()


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_connection():
    """Test Snowflake connection."""
    print_section("1. Testing Snowflake Connection")

    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        print("❌ Snowflake is not connected!")
        print("\nPossible issues:")
        print("1. ENABLE_SNOWFLAKE is not set to 'true' in .env")
        print("2. Snowflake credentials are incorrect")
        print("3. snowflake-connector-python is not installed")
        print("\nTo fix:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your Snowflake credentials")
        print("  3. Run: pip install snowflake-connector-python")
        return False

    print("✓ Connected to Snowflake!")

    # Get health check
    health = snowflake.health_check()
    print(f"\nDatabase: {health.get('database')}")
    print(f"Schema: {health.get('schema')}")
    print(f"Warehouse: {health.get('warehouse')}")
    print(f"Version: {health.get('version')}")

    return True


def test_insert_sample_commit():
    """Test inserting a sample commit."""
    print_section("2. Testing Commit Insertion")

    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        print("❌ Skipped - not connected")
        return False

    sample_commit = {
        "commit_hash": "abc123def456789012345678901234567890abcd",
        "repo_name": "test/bugrewind",
        "author": "Test User",
        "author_email": "test@example.com",
        "timestamp": "2024-01-15T10:30:00",
        "message": "Test commit for Snowflake integration",
        "files_changed": ["test.py", "README.md"],
        "insertions": 10,
        "deletions": 5
    }

    try:
        success = snowflake.insert_commit(sample_commit)

        if success:
            print("✓ Sample commit inserted successfully!")
            print(f"  Commit: {sample_commit['commit_hash'][:10]}")
            print(f"  Repo: {sample_commit['repo_name']}")
            print(f"  Author: {sample_commit['author']}")
            return True
        else:
            print("❌ Failed to insert commit")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you've run the SQL setup from SNOWFLAKE_INTEGRATION.md")
        return False


def test_search_commits():
    """Test searching commits."""
    print_section("3. Testing Commit Search")

    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        print("❌ Skipped - not connected")
        return False

    try:
        results = snowflake.search_commits(
            repo_name="test/bugrewind",
            limit=5
        )

        print(f"✓ Found {len(results)} commits")

        if results:
            print("\nSample results:")
            for commit in results[:3]:
                print(f"  - {commit.get('SHORT_HASH')}: {commit.get('MESSAGE')[:50]}...")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cortex_sentiment():
    """Test Cortex SENTIMENT function."""
    print_section("4. Testing Cortex SENTIMENT")

    if os.getenv("ENABLE_CORTEX_LLM", "false").lower() != "true":
        print("⚠ Cortex LLM is disabled")
        print("  Set ENABLE_CORTEX_LLM=true in .env to enable")
        return False

    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        print("❌ Skipped - not connected")
        return False

    try:
        # Get a commit to analyze
        results = snowflake.search_commits("test/bugrewind", limit=1)

        if not results:
            print("⚠ No commits found to analyze")
            return False

        commit_id = results[0]["COMMIT_ID"]
        sentiment = snowflake.analyze_commit_sentiment(commit_id)

        if sentiment:
            print("✓ Sentiment analysis successful!")
            print(f"  Commit: {sentiment['commit_id'][:10]}")
            print(f"  Score: {sentiment['sentiment_score']:.2f}")
            print(f"  Label: {sentiment['sentiment_label']}")
            print(f"  Panic fix: {sentiment['is_panic_fix']}")
            return True
        else:
            print("❌ Sentiment analysis failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nNote: Cortex functions require Snowflake Enterprise edition")
        return False


def test_cortex_search():
    """Test Cortex Search."""
    print_section("5. Testing Cortex Search")

    if os.getenv("ENABLE_CORTEX_SEARCH", "false").lower() != "true":
        print("⚠ Cortex Search is disabled")
        print("  Set ENABLE_CORTEX_SEARCH=true in .env to enable")
        return False

    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        print("❌ Skipped - not connected")
        return False

    try:
        results = snowflake.cortex_search_commits(
            query="test integration",
            limit=5
        )

        print(f"✓ Cortex search returned {len(results)} results")

        if results:
            print("\nTop results:")
            for result in results[:3]:
                score = result.get('SEARCH_SCORE', 0)
                message = result.get('MESSAGE', '')[:50]
                print(f"  - Score {score:.2f}: {message}...")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nNote: Make sure COMMIT_SEARCH service is created (see SNOWFLAKE_INTEGRATION.md)")
        return False


def test_repository_stats():
    """Test repository statistics."""
    print_section("6. Testing Repository Statistics")

    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        print("❌ Skipped - not connected")
        return False

    try:
        stats = snowflake.get_repository_stats("test/bugrewind")

        if stats:
            print("✓ Repository statistics retrieved!")
            print(f"  Total commits: {stats.get('TOTAL_COMMITS', 0)}")
            print(f"  Unique authors: {stats.get('UNIQUE_AUTHORS', 0)}")
            print(f"  Total insertions: {stats.get('TOTAL_INSERTIONS', 0)}")
            print(f"  Total deletions: {stats.get('TOTAL_DELETIONS', 0)}")
            return True
        else:
            print("⚠ No statistics available (no commits in repo)")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  BugRewind - Snowflake Integration Test")
    print("=" * 60)

    results = []

    # Test 1: Connection
    results.append(("Connection", test_connection()))

    if not results[0][1]:
        print("\n❌ Cannot proceed without Snowflake connection")
        print("\nSetup instructions:")
        print("1. Create Snowflake account at https://signup.snowflake.com/")
        print("2. Run the SQL setup from SNOWFLAKE_INTEGRATION.md")
        print("3. Configure .env with your credentials")
        print("4. Install: pip install snowflake-connector-python")
        return

    # Test 2-6: Features
    results.append(("Insert Commit", test_insert_sample_commit()))
    results.append(("Search Commits", test_search_commits()))
    results.append(("Cortex Sentiment", test_cortex_sentiment()))
    results.append(("Cortex Search", test_cortex_search()))
    results.append(("Repository Stats", test_repository_stats()))

    # Summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n*** All tests passed! Snowflake integration is working perfectly!")
    elif passed >= total - 2:
        print("\n*** Basic functionality working! Some advanced features may need setup.")
    else:
        print("\n*** Some tests failed. Check the errors above and:")
        print("  1. Verify Snowflake credentials in .env")
        print("  2. Ensure SQL tables are created (SNOWFLAKE_INTEGRATION.md)")
        print("  3. Check if Cortex features are enabled on your account")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
