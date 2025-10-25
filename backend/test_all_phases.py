#!/usr/bin/env python3
"""
Complete Test Suite: All Phases (PM Copilot with Vector Search)

Tests:
Phase 1: Elasticsearch + Vector Embeddings
Phase 2: Impact Set Analysis (Co-change + Ownership)
Phase 3: Hybrid Search (BM25 + kNN)
Phase 4: Graph Explore (Visual Impact Map)
"""
import sys
from app.config import config
from app.elastic.client import elastic_client
from app.elastic.indexer import commit_indexer
from app.elastic.files_indexer import files_indexer
from app.elastic.search import hybrid_searcher
from app.elastic.graph import graph_explorer
from app.git.analyzer import GitAnalyzer
from app.embeddings.client import embedding_client


def test_elasticsearch_connection():
    """Phase 1 Test 1: Verify Elasticsearch connection."""
    print("\n" + "="*70)
    print("PHASE 1 - TEST 1: Elasticsearch Connection")
    print("="*70)

    missing = config.validate()
    if missing:
        print(f"❌ Missing configuration: {', '.join(missing)}")
        return False

    print(f"Connecting to: {config.ELASTIC_ENDPOINT}")
    if elastic_client.ping():
        print("✅ Elasticsearch connection successful!")
        return True
    else:
        print("❌ Elasticsearch connection failed!")
        return False


def test_embeddings():
    """Phase 1 Test 2: Test embedding generation."""
    print("\n" + "="*70)
    print("PHASE 1 - TEST 2: Embedding Generation")
    print("="*70)

    test_texts = [
        "Fix authentication bug in login handler",
        "Add validation to user input form",
        "Refactor database connection pool"
    ]

    try:
        embeddings = embedding_client.embed_batch(test_texts)

        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"   Embedding dimensions: {len(embeddings[0])}")
        print(f"   Expected dimensions: {embedding_client.embedding_dim}")

        if len(embeddings[0]) == embedding_client.embedding_dim:
            print("✅ Embedding dimensions correct!")
            return True
        else:
            print("❌ Embedding dimensions mismatch!")
            return False

    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False


def test_index_creation():
    """Phase 1 Test 3: Create commits and files indices."""
    print("\n" + "="*70)
    print("PHASE 1 - TEST 3: Index Creation (Commits + Files)")
    print("="*70)

    try:
        # Create commits index
        commit_indexer.create_index(delete_if_exists=True)
        print(f"✅ Commits index '{config.ELASTIC_INDEX_NAME}' created")

        # Create files index
        files_indexer.create_index(delete_if_exists=True)
        print(f"✅ Files index 'files' created")

        return True
    except Exception as e:
        print(f"❌ Index creation failed: {e}")
        return False


def test_repo_indexing_with_embeddings(repo_url: str, max_commits: int = 50):
    """Phase 1 Test 4: Clone repo, extract commits, generate embeddings, index."""
    print("\n" + "="*70)
    print("PHASE 1 - TEST 4: Repository Indexing with Embeddings")
    print("="*70)

    analyzer = None
    try:
        analyzer = GitAnalyzer(repo_url)
        print(f"\nRepository: {analyzer.repo_name}")

        # Clone
        print("\n--- Cloning Repository ---")
        analyzer.clone_repo()
        print("✅ Repository cloned")

        # Extract commits WITH embeddings
        print(f"\n--- Extracting Commits (max {max_commits}) ---")
        commits = analyzer.get_all_commits(
            max_commits=max_commits,
            generate_embeddings=True  # NEW: Generate embeddings
        )
        print(f"✅ Extracted {len(commits)} commits with embeddings")

        # Verify embeddings exist
        if commits and 'message_embedding' in commits[0]:
            print(f"✅ Embeddings present in commit data")
            print(f"   Sample embedding length: {len(commits[0]['message_embedding'])}")
        else:
            print("⚠️  No embeddings found in commit data!")

        # Bulk index
        print("\n--- Indexing Commits ---")
        success, errors = commit_indexer.bulk_index_commits(commits)
        print(f"✅ Indexed {success} commits")
        if errors > 0:
            print(f"⚠️  {errors} errors")

        commit_indexer.refresh_index()

        # Store commits for Phase 2
        return commits

    except Exception as e:
        print(f"❌ Repository indexing failed: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if analyzer:
            analyzer.cleanup()


def test_impact_set_analysis(commits):
    """Phase 2 Test: Build files index with co-change analysis."""
    print("\n" + "="*70)
    print("PHASE 2: Impact Set Analysis (Co-Change + Ownership)")
    print("="*70)

    if not commits:
        print("❌ No commits available from Phase 1")
        return False

    try:
        # Build files index
        repo_id = commits[0]['repo_name']
        file_count = files_indexer.build_from_commits(commits, repo_id)

        print(f"\n✅ Indexed {file_count} files with:")
        print("   - Code ownership (top-3 contributors)")
        print("   - Co-change scores (Jaccard similarity)")
        print("   - Recent churn (30-day commit count)")
        print("   - Test file relationships")

        files_indexer.refresh_index()

        # Test impact set retrieval
        print("\n--- Testing Impact Set Retrieval ---")

        # Get a sample file
        sample_files = set()
        for commit in commits[:10]:
            for file_info in commit.get('files_changed', []):
                if isinstance(file_info, dict):
                    sample_files.add(file_info['path'])

        if sample_files:
            test_file = list(sample_files)[0]
            print(f"Testing impact set for: {test_file}")

            impact = files_indexer.get_impact_set(test_file, repo_id, min_co_change_score=0.3)

            if impact:
                print(f"✅ Impact set retrieved:")
                print(f"   Owners: {len(impact.get('owners', []))}")
                print(f"   Related files: {len(impact.get('related_files', []))}")
                print(f"   Test dependencies: {len(impact.get('test_dependencies', []))}")

                # Show top related files
                for related in impact.get('related_files', [])[:3]:
                    print(f"   - {related['file']} (score: {related['score']})")

        return True

    except Exception as e:
        print(f"❌ Impact set analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_search():
    """Phase 3 Test: Hybrid search (BM25 + kNN)."""
    print("\n" + "="*70)
    print("PHASE 3: Hybrid Search (BM25 + Vector kNN)")
    print("="*70)

    test_queries = [
        "authentication bug",
        "fix validation error",
        "refactor database"
    ]

    try:
        for query_text in test_queries:
            print(f"\n--- Query: '{query_text}' ---")

            # Generate query embedding
            query_vector = embedding_client.embed_text(query_text)

            # Hybrid search
            results = hybrid_searcher.hybrid_search(
                query_text=query_text,
                query_vector=query_vector,
                size=5
            )

            hits = results['hits']['hits']
            print(f"✅ Found {results['hits']['total']['value']} results (showing {len(hits)})")

            for i, hit in enumerate(hits, 1):
                fields = hit['fields']
                message = fields.get('message', [''])[0]
                author = fields.get('author_name', ['Unknown'])[0]
                print(f"   {i}. {message[:60]}... (by {author})")

            # Show aggregations
            aggs = results.get('aggregations', {})
            if 'impacted_files' in aggs:
                file_buckets = aggs['impacted_files'].get('file_paths', {}).get('buckets', [])
                print(f"   Top files: {len(file_buckets)} unique files impacted")

        print("\n✅ Hybrid search working!")
        return True

    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_explore():
    """Phase 4 Test: Graph explore for visual impact map."""
    print("\n" + "="*70)
    print("PHASE 4: Graph Explore (Visual Co-Change Network)")
    print("="*70)

    try:
        # Get a sample file from index
        sample_query = {
            "size": 1,
            "query": {"match_all": {}},
            "collapse": {
                "field": "files_changed.path.keyword"
            }
        }

        response = elastic_client.get_client().search(
            index=config.ELASTIC_INDEX_NAME,
            body=sample_query
        )

        if not response['hits']['hits']:
            print("⚠️  No commits found for graph exploration")
            return False

        # Extract a file path
        first_commit = response['hits']['hits'][0]
        files_changed = first_commit['_source'].get('files_changed', [])

        if not files_changed:
            print("⚠️  No files in sample commit")
            return False

        start_file = files_changed[0]['path']
        repo_id = first_commit['_source']['repo_name']

        print(f"Exploring co-change network for: {start_file}")

        # Graph explore
        graph = graph_explorer.get_file_neighborhood(
            file_path=start_file,
            repo_id=repo_id,
            radius=1
        )

        print(f"\n✅ Graph explore results:")
        print(f"   Vertices (files): {len(graph['vertices'])}")
        print(f"   Connections (co-changes): {len(graph['connections'])}")
        print(f"   Query time: {graph.get('took_ms', 0)}ms")

        # Show top connections
        for vertex in graph['vertices'][:5]:
            print(f"   - {vertex['label']} (weight: {vertex['weight']:.2f})")

        return True

    except Exception as e:
        print(f"❌ Graph explore failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_search_only():
    """Bonus Test: Pure kNN vector search."""
    print("\n" + "="*70)
    print("BONUS: Pure Vector Search (kNN only)")
    print("="*70)

    try:
        query_text = "authentication security fix"
        query_vector = embedding_client.embed_text(query_text)

        print(f"Query: '{query_text}'")

        results = hybrid_searcher.vector_search_only(
            query_vector=query_vector,
            k=5
        )

        hits = results['hits']['hits']
        print(f"✅ Found {len(hits)} semantic matches:")

        for i, hit in enumerate(hits, 1):
            fields = hit['fields']
            message = fields.get('message', [''])[0]
            score = hit.get('_score', 0)
            print(f"   {i}. {message[:60]}... (score: {score:.3f})")

        return True

    except Exception as e:
        print(f"❌ Vector search failed: {e}")
        return False


def main():
    """Run all phase tests."""
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "COMPLETE TEST SUITE" + " "*29 + "║")
    print("║" + " "*10 + "PM Copilot with Vector Search & Impact Analysis" + " "*11 + "║")
    print("╚" + "="*68 + "╝")

    # Configuration
    test_repo = "https://github.com/bentoml/BentoML"
    max_commits = 50

    results = []

    # Phase 1: Core Setup
    print("\n" + "#"*70)
    print("# PHASE 1: Elasticsearch + Vector Embeddings")
    print("#"*70)

    results.append(("Elasticsearch Connection", test_elasticsearch_connection()))

    if not results[-1][1]:
        print("\n⚠️  Cannot continue without Elasticsearch connection")
        sys.exit(1)

    results.append(("Embedding Generation", test_embeddings()))
    results.append(("Index Creation", test_index_creation()))

    commits = test_repo_indexing_with_embeddings(test_repo, max_commits)
    results.append(("Repository Indexing + Embeddings", commits is not None))

    # Phase 2: Impact Set Analysis
    if commits:
        print("\n" + "#"*70)
        print("# PHASE 2: Impact Set Analysis")
        print("#"*70)
        results.append(("Impact Set Analysis", test_impact_set_analysis(commits)))

    # Phase 3: Hybrid Search
    print("\n" + "#"*70)
    print("# PHASE 3: Hybrid Search")
    print("#"*70)
    results.append(("Hybrid Search (BM25 + kNN)", test_hybrid_search()))
    results.append(("Vector Search Only", test_vector_search_only()))

    # Phase 4: Graph Explore
    print("\n" + "#"*70)
    print("# PHASE 4: Graph Explore")
    print("#"*70)
    results.append(("Graph Explore", test_graph_explore()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    phase_results = {
        "Phase 1": [],
        "Phase 2": [],
        "Phase 3": [],
        "Phase 4": []
    }

    phase_mapping = {
        0: "Phase 1", 1: "Phase 1", 2: "Phase 1", 3: "Phase 1",
        4: "Phase 2",
        5: "Phase 3", 6: "Phase 3",
        7: "Phase 4"
    }

    for i, (test_name, passed) in enumerate(results):
        phase = phase_mapping.get(i, "Phase 1")
        phase_results[phase].append((test_name, passed))

    for phase, tests in phase_results.items():
        if not tests:
            continue

        print(f"\n{phase}:")
        for test_name, passed in tests:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} - {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n{'='*70}")
    print(f"Overall Results: {passed}/{total} tests passed")
    print(f"{'='*70}")

    if passed == total:
        print("\n🎉 ALL PHASES COMPLETE! System ready for PM copilot integration.")
        print("\nWhat's been built:")
        print("✅ Elasticsearch with vector embeddings (1024-dim)")
        print("✅ Hybrid search (BM25 + kNN)")
        print("✅ Impact set analysis (co-change + ownership)")
        print("✅ Graph explore for visual maps")
        print("\nNext steps:")
        print("1. Integrate with Postman Flow")
        print("2. Add Claude API for patch generation")
        print("3. Build GitHub PR + Asana task automation")
        print("4. Create Slack integration")
    else:
        print("\n⚠️  Some tests failed. Review logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
