#!/usr/bin/env python3
"""
Phase 1 Test Script: Elasticsearch Setup & Basic Indexing

Tests:
1. Elasticsearch connection
2. Index creation
3. Repository cloning
4. Commit extraction
5. Bulk indexing
6. Basic search queries
"""
import sys
from app.config import config
from app.elastic.client import elastic_client
from app.elastic.indexer import commit_indexer
from app.git.analyzer import GitAnalyzer


def test_elasticsearch_connection():
    """Test 1: Verify Elasticsearch connection."""
    print("\n" + "="*60)
    print("TEST 1: Elasticsearch Connection")
    print("="*60)

    # Validate config
    missing = config.validate()
    if missing:
        print(f"❌ Missing configuration: {', '.join(missing)}")
        print("\nPlease set these in backend/.env file:")
        for key in missing:
            print(f"  {key}=your_value_here")
        return False

    # Test connection
    print(f"Connecting to: {config.ELASTIC_ENDPOINT}")
    if elastic_client.ping():
        print("✅ Elasticsearch connection successful!")
        return True
    else:
        print("❌ Elasticsearch connection failed!")
        return False


def test_index_creation():
    """Test 2: Create the commits index."""
    print("\n" + "="*60)
    print("TEST 2: Index Creation")
    print("="*60)

    try:
        # Create index (delete if exists for clean test)
        created = commit_indexer.create_index(delete_if_exists=True)
        if created:
            print(f"✅ Index '{config.ELASTIC_INDEX_NAME}' created successfully!")
        else:
            print(f"ℹ️  Index '{config.ELASTIC_INDEX_NAME}' already exists")
        return True
    except Exception as e:
        print(f"❌ Index creation failed: {e}")
        return False


def test_repo_indexing(repo_url: str, max_commits: int = 100):
    """Test 3-5: Clone repo, extract commits, and index them."""
    print("\n" + "="*60)
    print("TEST 3-5: Repository Indexing")
    print("="*60)

    analyzer = None
    try:
        # Initialize analyzer
        analyzer = GitAnalyzer(repo_url)
        print(f"\nRepository: {analyzer.repo_name}")

        # Clone repository
        print("\n--- Cloning Repository ---")
        analyzer.clone_repo()
        print("✅ Repository cloned successfully!")

        # Extract commits
        print(f"\n--- Extracting Commits (max {max_commits}) ---")
        commits = analyzer.get_all_commits(max_commits=max_commits)
        print(f"✅ Extracted {len(commits)} commits")

        # Show sample commit
        if commits:
            sample = commits[0]
            print(f"\nSample commit:")
            print(f"  SHA: {sample['sha'][:8]}")
            print(f"  Author: {sample['author_name']}")
            print(f"  Date: {sample['commit_date']}")
            print(f"  Message: {sample['message'][:60]}...")
            print(f"  Files changed: {sample['files_count']}")

        # Bulk index commits
        print("\n--- Indexing Commits ---")
        success, errors = commit_indexer.bulk_index_commits(commits)
        print(f"✅ Indexed {success} commits")
        if errors > 0:
            print(f"⚠️  {errors} errors occurred")

        # Refresh index for immediate search
        commit_indexer.refresh_index()

        # Show index stats
        stats = commit_indexer.get_index_stats()
        print(f"\nIndex Statistics:")
        print(f"  Documents: {stats.get('document_count', 0)}")
        print(f"  Size: {stats.get('size_bytes', 0):,} bytes")

        return True

    except Exception as e:
        print(f"❌ Repository indexing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if analyzer:
            analyzer.cleanup()


def test_basic_search():
    """Test 6: Verify search functionality."""
    print("\n" + "="*60)
    print("TEST 6: Basic Search Queries")
    print("="*60)

    client = elastic_client.get_client()
    index = config.ELASTIC_INDEX_NAME

    try:
        # Query 1: Get all documents (limited)
        print("\n--- Query 1: Recent Commits ---")
        result = client.search(
            index=index,
            body={
                "size": 5,
                "sort": [{"commit_date": "desc"}],
                "query": {"match_all": {}}
            }
        )
        print(f"✅ Found {result['hits']['total']['value']} total commits")
        print(f"Showing {len(result['hits']['hits'])} most recent:")
        for hit in result['hits']['hits']:
            commit = hit['_source']
            print(f"  - {commit['sha'][:8]} | {commit['author_name']} | {commit['message'][:50]}")

        # Query 2: Search by author
        print("\n--- Query 2: Search by Author ---")
        if result['hits']['hits']:
            author = result['hits']['hits'][0]['_source']['author_name']
            result = client.search(
                index=index,
                body={
                    "query": {
                        "match": {"author_name": author}
                    }
                }
            )
            print(f"✅ Found {result['hits']['total']['value']} commits by '{author}'")

        # Query 3: Search in commit messages
        print("\n--- Query 3: Search Commit Messages ---")
        result = client.search(
            index=index,
            body={
                "size": 3,
                "query": {
                    "match": {"message": "fix"}  # Common word in commits
                }
            }
        )
        print(f"✅ Found {result['hits']['total']['value']} commits with 'fix' in message")
        for hit in result['hits']['hits'][:3]:
            commit = hit['_source']
            print(f"  - {commit['message'][:60]}...")

        return True

    except Exception as e:
        print(f"❌ Search queries failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 1 tests."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "PHASE 1 TEST SUITE" + " "*25 + "║")
    print("║" + " "*10 + "Elasticsearch Setup & Basic Indexing" + " "*12 + "║")
    print("╚" + "="*58 + "╝")

    # Test repository - using a small public repo
    test_repo = "https://github.com/bentoml/BentoML"  # Popular ML serving framework
    max_commits = 50  # Keep test small and fast

    results = []

    # Run tests
    results.append(("Elasticsearch Connection", test_elasticsearch_connection()))

    if results[-1][1]:  # Only continue if connection successful
        results.append(("Index Creation", test_index_creation()))
        results.append(("Repository Indexing", test_repo_indexing(test_repo, max_commits)))
        results.append(("Basic Search", test_basic_search()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 Phase 1 Complete! All tests passed.")
        print("\nNext steps:")
        print("1. Commit this phase: git add . && git commit -m 'Phase 1: Elastic setup and indexing'")
        print("2. Proceed to Phase 2: Search optimization")
    else:
        print("\n⚠️  Some tests failed. Please check configuration and logs.")
        sys.exit(1)


if __name__ == "__main__":
    main()
