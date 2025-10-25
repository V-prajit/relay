"""Index a git repository into Elasticsearch."""
import sys
from app.git.analyzer import GitAnalyzer
from app.elastic.indexer import es_indexer
from app.elastic.files_indexer import files_indexer


def index_repository(repo_url, max_commits=50):
    """Index a git repository."""

    print(f"Indexing repository: {repo_url}")
    print(f"Max commits: {max_commits}\n")

    analyzer = GitAnalyzer(repo_url)
    try:
        analyzer.clone_repo()
        commits = analyzer.get_all_commits(
            max_commits=max_commits,
            generate_embeddings=True
        )

        print(f"\n✓ Extracted {len(commits)} commits")

        print("\nIndexing commits...")
        es_indexer.bulk_index_commits(commits)
        print("✓ Commits indexed")

        print("\nBuilding file metadata...")
        files_indexer.build_from_commits(
            commits,
            repo_id=analyzer.repo_name
        )
        print("✓ File metadata indexed")

        print(f"\n✅ Successfully indexed {repo_url}")
        print(f"\nNext steps:")
        print("1. Test search: python test_search.py")
        print("2. Start server: python app/main.py")
        print("3. Visit: http://localhost:8000/docs")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        analyzer.cleanup()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python index_repo.py <repo_url> [max_commits]")
        print("\nExamples:")
        print("  python index_repo.py https://github.com/facebook/react 50")
        print("  python index_repo.py https://github.com/tj/commander.js 100")
        print("\nNote: Start with small repos (50-100 commits) for testing")
        sys.exit(1)

    repo_url = sys.argv[1]
    max_commits = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    index_repository(repo_url, max_commits)
