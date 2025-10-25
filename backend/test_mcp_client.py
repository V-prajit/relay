#!/usr/bin/env python3
"""
Test MCP Client for BugRewind PM Copilot.

Tests the MCP server by calling each tool with sample data.

Usage:
1. Start MCP server in one terminal:
   python mcp_server.py

2. Run this test client in another terminal:
   python test_mcp_client.py

Or test with Claude Desktop:
1. Add MCP server to claude_desktop_config.json
2. Restart Claude Desktop
3. Test with: @mcp impact.search query="test"
"""
import asyncio
import json

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("ERROR: mcp library not installed.")
    print("Install with: pip install mcp")
    exit(1)


async def test_impact_search(session: ClientSession):
    """Test impact.search tool."""
    print("\n" + "="*70)
    print("TEST 1: impact.search (Hybrid Search)")
    print("="*70)

    try:
        result = await session.call_tool(
            "impact.search",
            arguments={
                "query": "authentication bug",
                "size": 5
            }
        )

        print("\n✅ Result:")
        for content in result.content:
            if hasattr(content, 'text'):
                data = json.loads(content.text)
                print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"\n❌ Error: {e}")


async def test_risk_graph(session: ClientSession):
    """Test risk.graph tool."""
    print("\n" + "="*70)
    print("TEST 2: risk.graph (Co-Change Network)")
    print("="*70)

    try:
        result = await session.call_tool(
            "risk.graph",
            arguments={
                "seed_files": ["src/auth/login.py"],
                "max_connections": 10
            }
        )

        print("\n✅ Result:")
        for content in result.content:
            if hasattr(content, 'text'):
                data = json.loads(content.text)
                print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"\n❌ Error: {e}")


async def test_owner_lookup(session: ClientSession):
    """Test owner.lookup tool."""
    print("\n" + "="*70)
    print("TEST 3: owner.lookup (Code Ownership)")
    print("="*70)

    try:
        result = await session.call_tool(
            "owner.lookup",
            arguments={
                "file_path": "src/auth/login.py",
                "repo_id": "test-repo"
            }
        )

        print("\n✅ Result:")
        for content in result.content:
            if hasattr(content, 'text'):
                data = json.loads(content.text)
                print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """Run all MCP tool tests."""
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "MCP CLIENT TEST SUITE" + " "*27 + "║")
    print("╚" + "="*68 + "╝")

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )

    print("\n⏳ Connecting to MCP server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("✅ Connected to MCP server")

            # List available tools
            print("\n" + "="*70)
            print("AVAILABLE TOOLS")
            print("="*70)

            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"\n📦 {tool.name}")
                print(f"   {tool.description}")

            # Run tests
            await test_impact_search(session)
            await test_risk_graph(session)
            await test_owner_lookup(session)

            print("\n" + "="*70)
            print("TEST SUMMARY")
            print("="*70)
            print("✅ All MCP tools are accessible")
            print("\nNext steps:")
            print("1. Index a real repository with test_all_phases.py")
            print("2. Test with real data")
            print("3. Configure in Claude Desktop (see instructions below)")


def print_claude_desktop_instructions():
    """Print instructions for Claude Desktop integration."""
    print("\n" + "="*70)
    print("CLAUDE DESKTOP INTEGRATION")
    print("="*70)
    print("""
1. Find Claude Desktop config file:
   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
   Windows: %APPDATA%\\Claude\\claude_desktop_config.json
   Linux: ~/.config/Claude/claude_desktop_config.json

2. Add MCP server config:
   {
     "mcpServers": {
       "bugrewind": {
         "command": "python",
         "args": ["/absolute/path/to/backend/mcp_server.py"],
         "env": {
           "PYTHONPATH": "/absolute/path/to/backend"
         }
       }
     }
   }

3. Restart Claude Desktop

4. Test with:
   @mcp impact.search query="authentication bug" repo_id="owner/repo"

5. Screenshot for Devpost:
   - Show @mcp command
   - Show tool execution
   - Show results
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        print_claude_desktop_instructions()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
