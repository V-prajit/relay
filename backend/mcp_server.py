#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for BugRewind PM Copilot.

Exposes Elasticsearch-backed tools via MCP for use with:
- Claude Desktop
- Cursor
- Any MCP-compatible client

Tools:
- impact.search: Hybrid search (BM25 + kNN + ELSER)
- risk.graph: Co-change network exploration
- owner.lookup: Code ownership and impact analysis

Usage with Claude Desktop:
1. Add to ~/.config/Claude/claude_desktop_config.json:
   {
     "mcpServers": {
       "bugrewind": {
         "command": "python",
         "args": ["/path/to/backend/mcp_server.py"]
       }
     }
   }

2. Restart Claude Desktop

3. Test: @mcp impact.search query="authentication bug" repo_id="my-repo"
"""
import asyncio
import json
from typing import Any

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: mcp library not installed.")
    print("Install with: pip install mcp")
    exit(1)

# BugRewind imports
from app.config import config
from app.elastic.search import hybrid_searcher
from app.elastic.graph import graph_explorer
from app.elastic.files_indexer import files_indexer
from app.embeddings.client import embedding_client


# Initialize MCP server
server = Server("bugrewind-pm-copilot")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available MCP tools."""
    return [
        types.Tool(
            name="impact.search",
            description="Search commits using hybrid retrieval (BM25 + kNN + ELSER). "
                       "Finds relevant commits by combining keyword matching, semantic similarity, "
                       "and learned term expansions. Returns commits with scores and impacted files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'authentication bug', 'fix validation')"
                    },
                    "repo_id": {
                        "type": "string",
                        "description": "Repository identifier (e.g., 'owner/repo'). Optional."
                    },
                    "size": {
                        "type": "number",
                        "description": "Number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="risk.graph",
            description="Explore co-change network from seed files using Elasticsearch Graph API. "
                       "Finds files that frequently change together, useful for understanding "
                       "impact and dependencies. Returns graph with vertices (files) and connections.",
            inputSchema={
                "type": "object",
                "properties": {
                    "seed_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Starting file paths to explore from (e.g., ['src/auth/login.py'])"
                    },
                    "repo_id": {
                        "type": "string",
                        "description": "Repository identifier. Optional."
                    },
                    "max_connections": {
                        "type": "number",
                        "description": "Maximum connections per vertex (default: 20)",
                        "default": 20
                    }
                },
                "required": ["seed_files"]
            }
        ),
        types.Tool(
            name="owner.lookup",
            description="Get code ownership and impact analysis for a file. "
                       "Returns top contributors, files that co-change with it, test dependencies, "
                       "and risk metrics. Useful for understanding who owns code and what else might break.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path to analyze (e.g., 'src/auth/login.py')"
                    },
                    "repo_id": {
                        "type": "string",
                        "description": "Repository identifier (e.g., 'owner/repo')"
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum co-change score threshold (0-1, default: 0.3)",
                        "default": 0.3
                    }
                },
                "required": ["file_path", "repo_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """Execute MCP tool."""

    if name == "impact.search":
        return await impact_search_tool(arguments)
    elif name == "risk.graph":
        return await risk_graph_tool(arguments)
    elif name == "owner.lookup":
        return await owner_lookup_tool(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def impact_search_tool(args: dict) -> list[types.TextContent]:
    """Hybrid search tool: BM25 + kNN + ELSER."""
    try:
        query = args["query"]
        repo_id = args.get("repo_id")
        size = args.get("size", 10)

        # Generate query embedding
        query_vector = embedding_client.embed_text(query)

        # Hybrid search
        results = hybrid_searcher.hybrid_search(
            query_text=query,
            query_vector=query_vector,
            repo_id=repo_id,
            size=size
        )

        # Format results
        hits = []
        for hit in results['hits']['hits']:
            fields = hit.get('fields', {})
            hits.append({
                'sha': fields.get('sha', [''])[0][:8],
                'message': fields.get('message', [''])[0],
                'author': fields.get('author_name', [''])[0],
                'date': fields.get('commit_date', [''])[0],
                'files': fields.get('files_changed.path', []),
                'score': hit.get('_score', 0)
            })

        # Extract top impacted files
        aggs = results.get('aggregations', {})
        impacted_files = []
        if 'impacted_files' in aggs:
            file_buckets = aggs['impacted_files'].get('file_paths', {}).get('buckets', [])
            impacted_files = [bucket['key'] for bucket in file_buckets[:5]]

        response = {
            "total_results": results['hits']['total']['value'],
            "hits": hits[:size],
            "impacted_files": impacted_files,
            "search_type": "hybrid (BM25 + kNN + ELSER)"
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def risk_graph_tool(args: dict) -> list[types.TextContent]:
    """Co-change graph exploration tool."""
    try:
        seed_files = args["seed_files"]
        repo_id = args.get("repo_id")
        max_connections = args.get("max_connections", 20)

        # Explore graph
        graph = graph_explorer.explore_co_change_network(
            start_files=seed_files,
            repo_id=repo_id,
            max_depth=2,
            max_connections=max_connections
        )

        response = {
            "seed_files": seed_files,
            "vertices_count": len(graph['vertices']),
            "connections_count": len(graph['connections']),
            "vertices": [
                {
                    "file": v['label'],
                    "weight": v['weight'],
                    "doc_count": v['doc_count']
                }
                for v in graph['vertices'][:10]  # Top 10 for readability
            ],
            "top_connections": [
                {
                    "source": c['source'],
                    "target": c['target'],
                    "weight": c['weight']
                }
                for c in graph['connections'][:10]
            ]
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def owner_lookup_tool(args: dict) -> list[types.TextContent]:
    """Code ownership and impact analysis tool."""
    try:
        file_path = args["file_path"]
        repo_id = args["repo_id"]
        min_score = args.get("min_score", 0.3)

        # Get impact set
        impact = files_indexer.get_impact_set(
            file_path=file_path,
            repo_id=repo_id,
            min_co_change_score=min_score
        )

        if not impact:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"File not found: {file_path}"}, indent=2)
            )]

        response = {
            "file_path": impact['file_path'],
            "owners": impact['owners'][:3],  # Top 3
            "related_files": impact['related_files'][:10],  # Top 10
            "test_dependencies": impact.get('test_dependencies', []),
            "recent_churn": impact.get('recent_churn', 0),
            "risk_level": "high" if impact.get('recent_churn', 0) > 5 else "medium" if impact.get('recent_churn', 0) > 2 else "low"
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main():
    """Run MCP server."""
    print("BugRewind MCP Server starting...", flush=True)
    print(f"Elasticsearch endpoint: {config.ELASTIC_ENDPOINT}", flush=True)
    print("Available tools:", flush=True)
    print("  - impact.search: Hybrid search (BM25 + kNN + ELSER)", flush=True)
    print("  - risk.graph: Co-change network exploration", flush=True)
    print("  - owner.lookup: Code ownership analysis", flush=True)
    print("\nListening for MCP requests via stdio...", flush=True)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
