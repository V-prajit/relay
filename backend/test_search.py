"""Test hybrid search functionality."""
from app.elastic.search import hybrid_searcher
from app.embeddings.client import embedding_client


def test_search():
    """Test hybrid search."""

    query = "fix bug"
    print(f"Searching for: '{query}'\n")

    query_vector = embedding_client.embed_text(query)
    print(f"✓ Query vector generated ({len(query_vector)} dimensions)")

    results = hybrid_searcher.hybrid_search(
        query_text=query,
        query_vector=query_vector,
        size=5
    )

    total = results['hits']['total']['value']
    print(f"✓ Found {total} total results\n")

    if total == 0:
        print("No results found. Make sure you've indexed a repository:")
        print("  python index_repo.py <repo_url> <max_commits>")
        return

    print("Top 5 commits:")
    for i, hit in enumerate(results['hits']['hits'][:5], 1):
        fields = hit.get('fields', {})
        sha = fields.get('sha', ['unknown'])[0][:8]
        message = fields.get('message', [''])[0][:60]
        score = hit.get('_score', 0)
        rank = hit.get('_rank', i)

        print(f"{rank}. [{sha}] {message}... (score: {score:.2f})")

    aggs = results.get('aggregations', {})
    if 'impacted_files' in aggs:
        file_buckets = aggs['impacted_files'].get('file_paths', {}).get('buckets', [])
        if file_buckets:
            print("\nTop impacted files:")
            for bucket in file_buckets[:5]:
                print(f"  - {bucket['key']} ({bucket['doc_count']} commits)")

    if 'top_authors' in aggs:
        author_buckets = aggs['top_authors'].get('buckets', [])
        if author_buckets:
            print("\nTop authors:")
            for bucket in author_buckets[:3]:
                print(f"  - {bucket['key']} ({bucket['doc_count']} commits)")

    print(f"\n✅ Hybrid search working! (BM25 + kNN + ELSER)")


if __name__ == "__main__":
    try:
        test_search()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
