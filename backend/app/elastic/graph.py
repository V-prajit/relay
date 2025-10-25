"""Elasticsearch Graph API for visual impact maps."""
from typing import Dict, Any, List, Optional
from elasticsearch import Elasticsearch

from app.elastic.client import elastic_client
from app.config import config


class GraphExplorer:
    """Elasticsearch Graph API wrapper for co-change visualization."""

    def __init__(self):
        """Initialize graph explorer."""
        self.client: Elasticsearch = elastic_client.get_client()
        self.commits_index = config.ELASTIC_INDEX_NAME

    def explore_co_change_network(
        self,
        start_files: List[str],
        repo_id: Optional[str] = None,
        max_depth: int = 2,
        max_connections: int = 20
    ) -> Dict[str, Any]:
        """Explore co-change network using Graph API.

        Args:
            start_files: Starting file paths
            repo_id: Optional repository filter
            max_depth: How many hops to traverse
            max_connections: Max connections per vertex

        Returns:
            Graph structure with vertices and connections
        """
        # Build base query
        query = {
            "nested": {
                "path": "files_changed",
                "query": {
                    "terms": {
                        "files_changed.path.keyword": start_files
                    }
                }
            }
        }

        if repo_id:
            query = {
                "bool": {
                    "must": [query],
                    "filter": [{"term": {"repo_name": repo_id}}]
                }
            }

        # Graph explore request
        graph_request = {
            "controls": {
                "use_significance": True,  # Boost unexpected connections
                "sample_size": 1000,  # Sample size for scoring
                "timeout": 5000  # 5 second timeout
            },
            "query": query,
            "vertices": [
                {
                    "field": "files_changed.path.keyword",
                    "size": max_connections,
                    "min_doc_count": 2  # File must appear in at least 2 commits
                }
            ],
            "connections": {
                "vertices": [
                    {
                        "field": "files_changed.path.keyword",
                        "size": max_connections
                    }
                ]
            }
        }

        try:
            response = self.client.graph.explore(
                index=self.commits_index,
                body=graph_request
            )

            return self._format_graph_response(response)

        except Exception as e:
            print(f"Graph explore error: {e}")
            return {"vertices": [], "connections": []}

    def _format_graph_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format Graph API response for frontend consumption.

        Args:
            response: Raw Elasticsearch Graph response

        Returns:
            Formatted graph with nodes and edges
        """
        vertices = []
        connections = []

        # Extract vertices (files)
        for vertex in response.get('vertices', []):
            vertices.append({
                'id': vertex['field'] + ':' + vertex['term'],
                'label': vertex['term'],  # File path
                'weight': vertex.get('weight', 1.0),
                'doc_count': vertex.get('doc_count', 0)
            })

        # Extract connections (co-changes)
        for connection in response.get('connections', []):
            source_idx = connection['source']
            target_idx = connection['target']

            if source_idx < len(vertices) and target_idx < len(vertices):
                connections.append({
                    'source': vertices[source_idx]['id'],
                    'target': vertices[target_idx]['id'],
                    'weight': connection.get('weight', 1.0),
                    'doc_count': connection.get('doc_count', 0)
                })

        return {
            'vertices': vertices,
            'connections': connections,
            'took_ms': response.get('took', 0)
        }

    def get_file_neighborhood(
        self,
        file_path: str,
        repo_id: Optional[str] = None,
        radius: int = 1
    ) -> Dict[str, Any]:
        """Get immediate neighborhood of a file (1-hop connections).

        Args:
            file_path: File to explore
            repo_id: Optional repository filter
            radius: Number of hops (1 or 2)

        Returns:
            Files that co-change with the given file
        """
        return self.explore_co_change_network(
            start_files=[file_path],
            repo_id=repo_id,
            max_depth=radius,
            max_connections=15
        )


# Global graph explorer instance
graph_explorer = GraphExplorer()
