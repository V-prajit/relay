"""Hybrid search queries combining BM25 and vector similarity (kNN)."""
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch

from app.elastic.client import elastic_client
from app.config import config


class HybridSearcher:
    """Hybrid search combining traditional BM25 and vector kNN search."""

    def __init__(self):
        """Initialize hybrid searcher."""
        self.client: Elasticsearch = elastic_client.get_client()
        self.index_name = config.ELASTIC_INDEX_NAME

    def hybrid_search(
        self,
        query_text: str,
        query_vector: List[float],
        repo_id: Optional[str] = None,
        size: int = 20,
        time_range_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """Perform hybrid search using RRF (Reciprocal Rank Fusion).

        Combines THREE retrieval methods:
        1. BM25: Lexical keyword matching
        2. kNN: Semantic similarity via dense vectors (1024-dim)
        3. ELSER: Learned sparse embeddings for explainable semantic search

        RRF automatically fuses scores without manual tuning.

        Args:
            query_text: Text query for BM25 search
            query_vector: 1024-dim embedding vector for kNN search
            repo_id: Optional filter by repository
            size: Number of results to return
            time_range_months: Optional filter by recent commits (e.g., 6 months)

        Returns:
            Search results with both BM25 and kNN matches
        """
        # Build filter conditions
        filters = []
        if repo_id:
            filters.append({"term": {"repo_name": repo_id}})

        if time_range_months:
            filters.append({
                "range": {
                    "commit_date": {
                        "gte": f"now-{time_range_months}M"
                    }
                }
            })

        filter_clause = {"bool": {"must": filters}} if filters else None

        # Build RRF retriever query with 3-way fusion: BM25 + kNN + ELSER
        query = {
            "retriever": {
                "rrf": {  # Reciprocal Rank Fusion
                    "retrievers": [
                        # 1. BM25 lexical search (keyword matching)
                        {
                            "standard": {
                                "query": {
                                    "bool": {
                                        "should": [
                                            {
                                                "multi_match": {
                                                    "query": query_text,
                                                    "fields": [
                                                        "message^3",  # Boost commit message
                                                        "author_name^2",  # Boost author
                                                        "files_changed.path"
                                                    ],
                                                    "type": "best_fields"
                                                }
                                            }
                                        ],
                                        "filter": filters if filters else []
                                    }
                                }
                            }
                        },
                        # 2. kNN dense vector similarity search (semantic)
                        {
                            "knn": {
                                "field": "message_embedding",
                                "query_vector": query_vector,
                                "k": 50,  # Retrieve top-50 for fusion
                                "num_candidates": 200,  # Search through 200 candidates
                                "filter": filter_clause
                            }
                        },
                        # 3. ELSER sparse embeddings (explainable semantic search)
                        {
                            "standard": {
                                "query": {
                                    "bool": {
                                        "should": [
                                            {
                                                "text_expansion": {
                                                    "message_expansion": {
                                                        "model_id": ".elser_model_2_linux-x86_64",
                                                        "model_text": query_text
                                                    }
                                                }
                                            }
                                        ],
                                        "filter": filters if filters else []
                                    }
                                }
                            }
                        }
                    ],
                    "rank_window_size": 100,  # Consider top-100 from each retriever
                    "rank_constant": 60  # RRF constant (default)
                }
            },
            "size": size,
            "fields": [
                "sha",
                "message",
                "author_name",
                "author_email",
                "commit_date",
                "files_changed.path",
                "files_changed.change_type",
                "total_additions",
                "total_deletions",
                "repo_name"
            ],
            "_source": False,  # Use fields instead of _source for efficiency
            "aggs": {
                "impacted_files": {
                    "nested": {
                        "path": "files_changed"
                    },
                    "aggs": {
                        "file_paths": {
                            "terms": {
                                "field": "files_changed.path.keyword",
                                "size": 50
                            }
                        }
                    }
                },
                "top_authors": {
                    "terms": {
                        "field": "author_name.keyword",
                        "size": 10
                    }
                }
            }
        }

        # Execute search
        response = self.client.search(
            index=self.index_name,
            body=query
        )

        return response

    def vector_search_only(
        self,
        query_vector: List[float],
        repo_id: Optional[str] = None,
        k: int = 10,
        num_candidates: int = 100
    ) -> Dict[str, Any]:
        """Perform pure kNN vector search (no BM25).

        Useful for semantic similarity when exact keyword matches aren't important.

        Args:
            query_vector: 1024-dim embedding vector
            repo_id: Optional filter by repository
            k: Number of nearest neighbors
            num_candidates: Number of candidates to consider

        Returns:
            Search results ranked by vector similarity
        """
        filter_clause = None
        if repo_id:
            filter_clause = {"term": {"repo_name": repo_id}}

        query = {
            "knn": {
                "field": "message_embedding",
                "query_vector": query_vector,
                "k": k,
                "num_candidates": num_candidates,
                "filter": filter_clause
            },
            "fields": [
                "sha",
                "message",
                "author_name",
                "commit_date",
                "files_changed.path"
            ],
            "_source": False
        }

        response = self.client.search(
            index=self.index_name,
            body=query
        )

        return response

    def bm25_search_only(
        self,
        query_text: str,
        repo_id: Optional[str] = None,
        size: int = 10
    ) -> Dict[str, Any]:
        """Perform traditional BM25 text search (no vectors).

        Useful for exact keyword matches, file names, author names.

        Args:
            query_text: Search query
            repo_id: Optional filter by repository
            size: Number of results

        Returns:
            BM25-ranked search results
        """
        filters = []
        if repo_id:
            filters.append({"term": {"repo_name": repo_id}})

        query = {
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query_text,
                            "fields": [
                                "message^3",
                                "author_name^2",
                                "files_changed.path"
                            ]
                        }
                    },
                    "filter": filters
                }
            },
            "size": size
        }

        response = self.client.search(
            index=self.index_name,
            body=query
        )

        return response

    def search_by_file_path(
        self,
        file_path: str,
        repo_id: Optional[str] = None,
        size: int = 50
    ) -> Dict[str, Any]:
        """Find all commits that modified a specific file.

        Args:
            file_path: Exact file path to search
            repo_id: Optional repository filter
            size: Number of results

        Returns:
            Commits that modified the file, sorted by date (most recent first)
        """
        filters = [
            {"term": {"files_changed.path.keyword": file_path}}
        ]

        if repo_id:
            filters.append({"term": {"repo_name": repo_id}})

        query = {
            "query": {
                "nested": {
                    "path": "files_changed",
                    "query": {
                        "bool": {
                            "filter": filters
                        }
                    }
                }
            },
            "sort": [
                {"commit_date": "desc"}
            ],
            "size": size
        }

        response = self.client.search(
            index=self.index_name,
            body=query
        )

        return response


# Global searcher instance
hybrid_searcher = HybridSearcher()
