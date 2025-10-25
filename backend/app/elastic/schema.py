"""Index schema definitions for Elasticsearch."""

# Commit index mapping - optimized for PM copilot with hybrid search
# Supports both traditional BM25 search and vector similarity (kNN)
COMMIT_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            # Commit metadata
            "sha": {
                "type": "keyword"  # Exact match for commit hashes
            },
            "author_name": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}  # For aggregations
                }
            },
            "author_email": {
                "type": "keyword"
            },
            "committer_name": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "committer_email": {
                "type": "keyword"
            },
            "commit_date": {
                "type": "date"
            },
            "message": {
                "type": "text",
                "analyzer": "standard"  # Full-text search on commit messages
            },
            "message_embedding": {
                "type": "dense_vector",
                "dims": 1024,  # Claude embeddings are 1024-dimensional
                "similarity": "cosine",
                "index": True,
                "index_options": {
                    "type": "int8_hnsw",  # Quantized for memory efficiency (4x reduction)
                    "m": 16,  # HNSW graph connections per node
                    "ef_construction": 100  # Build-time search depth
                }
            },

            # Repository info
            "repo_url": {
                "type": "keyword"
            },
            "repo_name": {
                "type": "keyword"
            },

            # File changes
            "files_changed": {
                "type": "nested",  # Array of file objects
                "properties": {
                    "path": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}  # Exact path matching
                        }
                    },
                    "change_type": {
                        "type": "keyword"  # A (added), M (modified), D (deleted)
                    },
                    "additions": {
                        "type": "integer"
                    },
                    "deletions": {
                        "type": "integer"
                    },
                    "diff": {
                        "type": "text",
                        "analyzer": "standard",  # Search in code diffs
                        "index": False  # Don't index diff content (too large)
                    }
                }
            },

            # Aggregate stats
            "total_additions": {
                "type": "integer"
            },
            "total_deletions": {
                "type": "integer"
            },
            "files_count": {
                "type": "integer"
            },

            # Parent commits (for traversing history)
            "parent_shas": {
                "type": "keyword"
            },

            # Indexing metadata
            "indexed_at": {
                "type": "date"
            }
        }
    },
    "settings": {}
}


# Files index mapping - for impact set analysis and code ownership
FILES_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "file_path": {
                "type": "keyword"  # Exact file paths
            },
            "repo_id": {
                "type": "keyword"
            },
            "extension": {
                "type": "keyword"  # .py, .js, .tsx, etc.
            },
            "is_test_file": {
                "type": "boolean"
            },

            # Code ownership - top contributors
            "owners": {
                "type": "nested",
                "properties": {
                    "author": {
                        "type": "keyword"
                    },
                    "author_name": {
                        "type": "text"
                    },
                    "commit_count": {
                        "type": "integer"
                    },
                    "last_touched": {
                        "type": "date"
                    },
                    "lines_changed": {
                        "type": "integer"  # Total additions + deletions
                    }
                }
            },

            # Co-change scores - files that change together
            # Stored as JSON object: {"other_file_path": score}
            "co_change_scores": {
                "type": "object",
                "enabled": False  # Don't index, just store
            },

            # Test relationships
            "test_dependencies": {
                "type": "keyword"  # Test files that exercise this file
            },
            "tests_for_files": {
                "type": "keyword"  # If this is a test, files it tests
            },

            # Risk metrics
            "recent_churn": {
                "type": "integer"  # Commits in last 30 days
            },
            "total_commits": {
                "type": "integer"
            },
            "avg_change_size": {
                "type": "float"  # Average lines changed per commit
            },

            # Metadata
            "first_seen": {
                "type": "date"
            },
            "last_modified": {
                "type": "date"
            },
            "indexed_at": {
                "type": "date"
            }
        }
    },
    "settings": {}
}
