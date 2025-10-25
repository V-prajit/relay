#!/usr/bin/env python3
"""
Register BugRewind tools in Elastic Agent Builder.

This script generates the configuration needed to register custom tools
in Elasticsearch Agent Builder and expose them via MCP.

Steps:
1. Run this script to generate tool configs
2. In Elastic Console, go to Agent Builder
3. Create new agent
4. Add custom tools using the generated configs
5. Expose via MCP endpoint

Tools registered:
- impact_search: Hybrid retrieval (BM25 + kNN + ELSER)
- risk_graph: Co-change network exploration
- owner_lookup: Code ownership and impact analysis
"""
import json
from app.config import config


# Tool configurations for Agent Builder
AGENT_BUILDER_TOOLS = {
    "impact_search": {
        "name": "impact_search",
        "description": "Search commits using hybrid retrieval combining BM25 keyword matching, "
                      "kNN semantic similarity, and ELSER learned embeddings. "
                      "Returns relevant commits with scores and impacted files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'authentication bug', 'fix validation error')"
                },
                "repo_id": {
                    "type": "string",
                    "description": "Repository identifier (e.g., 'owner/repo'). Optional."
                },
                "size": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 10
                }
            },
            "required": ["query"]
        },
        "endpoint": {
            "method": "POST",
            "url": "http://localhost:8000/api/search",
            "headers": {
                "Content-Type": "application/json"
            },
            "body_template": {
                "query": "{{query}}",
                "repo_id": "{{repo_id}}",
                "size": "{{size}}"
            }
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "total": {"type": "integer"},
                "hits": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sha": {"type": "string"},
                            "message": {"type": "string"},
                            "author": {"type": "string"},
                            "score": {"type": "number"}
                        }
                    }
                }
            }
        }
    },

    "risk_graph": {
        "name": "risk_graph",
        "description": "Explore co-change network from seed files using Elasticsearch Graph API. "
                      "Returns files that frequently change together, useful for understanding "
                      "dependencies and blast radius of changes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Seed file paths to explore from"
                },
                "repo_id": {
                    "type": "string",
                    "description": "Repository identifier. Optional."
                },
                "max_connections": {
                    "type": "integer",
                    "description": "Maximum connections per vertex",
                    "default": 20
                }
            },
            "required": ["files"]
        },
        "endpoint": {
            "method": "POST",
            "url": "http://localhost:8000/api/graph",
            "headers": {
                "Content-Type": "application/json"
            },
            "body_template": {
                "files": "{{files}}",
                "repo_id": "{{repo_id}}",
                "max_connections": "{{max_connections}}"
            }
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "vertices": {
                    "type": "array",
                    "description": "Files in the co-change network"
                },
                "connections": {
                    "type": "array",
                    "description": "Co-change relationships"
                }
            }
        }
    },

    "owner_lookup": {
        "name": "owner_lookup",
        "description": "Get code ownership and impact analysis for a file. "
                      "Returns top contributors, co-changing files, test dependencies, "
                      "and risk metrics. Useful for finding subject-matter experts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path to analyze"
                },
                "repo_id": {
                    "type": "string",
                    "description": "Repository identifier"
                },
                "min_co_change_score": {
                    "type": "number",
                    "description": "Minimum co-change score (0-1)",
                    "default": 0.3
                }
            },
            "required": ["file_path", "repo_id"]
        },
        "endpoint": {
            "method": "POST",
            "url": "http://localhost:8000/api/impact",
            "headers": {
                "Content-Type": "application/json"
            },
            "body_template": {
                "file_path": "{{file_path}}",
                "repo_id": "{{repo_id}}",
                "min_co_change_score": "{{min_co_change_score}}"
            }
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "owners": {
                    "type": "array",
                    "description": "Top contributors"
                },
                "related_files": {
                    "type": "array",
                    "description": "Files that co-change"
                },
                "risk_level": {"type": "string"}
            }
        }
    }
}


def generate_agent_builder_configs():
    """Generate Agent Builder tool configurations."""
    print("="*70)
    print("ELASTIC AGENT BUILDER - TOOL REGISTRATION CONFIGS")
    print("="*70)
    print()
    print("Copy these configurations to Elastic Agent Builder:")
    print()

    for tool_name, tool_config in AGENT_BUILDER_TOOLS.items():
        print(f"\n{'='*70}")
        print(f"TOOL: {tool_name}")
        print(f"{'='*70}")
        print(json.dumps(tool_config, indent=2))
        print()

    # Save to file
    output_file = "agent_builder_tools.json"
    with open(output_file, 'w') as f:
        json.dump(AGENT_BUILDER_TOOLS, f, indent=2)

    print(f"\n✅ Saved to: {output_file}")
    print()
    print("="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Start FastAPI server: python -m app.main")
    print("2. Go to Elastic Console → Agent Builder")
    print("3. Create new agent")
    print("4. For each tool above:")
    print("   - Click 'Add Tool'")
    print("   - Choose 'HTTP Connector'")
    print("   - Paste the endpoint config")
    print("   - Test the tool")
    print("5. Save agent and get MCP endpoint URL")
    print("6. Use MCP endpoint in Claude Desktop or Cursor")
    print()


def generate_mcp_config():
    """Generate Claude Desktop MCP configuration."""
    print("="*70)
    print("CLAUDE DESKTOP MCP CONFIGURATION")
    print("="*70)
    print()
    print("Add this to ~/.config/Claude/claude_desktop_config.json:")
    print()

    mcp_config = {
        "mcpServers": {
            "bugrewind": {
                "command": "python",
                "args": ["./backend/mcp_server.py"],
                "env": {
                    "ELASTIC_API_KEY": config.ELASTIC_API_KEY or "your_key_here",
                    "ELASTIC_ENDPOINT": config.ELASTIC_ENDPOINT or "your_endpoint_here"
                }
            }
        }
    }

    print(json.dumps(mcp_config, indent=2))
    print()
    print("Then restart Claude Desktop and test with:")
    print('  @mcp impact.search query="authentication bug"')
    print()


if __name__ == "__main__":
    generate_agent_builder_configs()
    print()
    generate_mcp_config()
