"""Create Elasticsearch indices."""
from app.elastic.client import elastic_client
from app.elastic.schema import COMMIT_INDEX_MAPPING, FILES_INDEX_MAPPING


def create_indices():
    """Create Elasticsearch indices."""

    client = elastic_client.get_client()

    commits_index = "commits"
    if not client.indices.exists(index=commits_index):
        print(f"Creating {commits_index} index...")
        client.indices.create(
            index=commits_index,
            body=COMMIT_INDEX_MAPPING
        )
        print(f"✓ {commits_index} index created")
    else:
        print(f"✓ {commits_index} index already exists")

    files_index = "files"
    if not client.indices.exists(index=files_index):
        print(f"Creating {files_index} index...")
        client.indices.create(
            index=files_index,
            body=FILES_INDEX_MAPPING
        )
        print(f"✓ {files_index} index created")
    else:
        print(f"✓ {files_index} index already exists")

    print("\n✅ All indices ready!")
    print("\nNext steps:")
    print("1. Run: python index_repo.py <repo_url> <max_commits>")
    print("2. Example: python index_repo.py https://github.com/facebook/react 50")


if __name__ == "__main__":
    create_indices()
