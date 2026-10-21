
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Project structure:
# restaurant-chatbot/
#   backend/mcp_client.py
#   mcp_server/server.py

PROJECT_ROOT = Path(__file__).resolve().parents[2]


SERVER_FILE = PROJECT_ROOT / "mcp_server" / "server.py"

# Use the MCP server's own virtual environment locally on Windows.
# On Render/Linux, use the Python executable running the backend.
if os.name == "nt":
    SERVER_PYTHON = (
        PROJECT_ROOT / "mcp_server" / ".venv" / "Scripts" / "python.exe"
    )
else:
    SERVER_PYTHON = sys.executable


SERVER_PYTHON = Path(SERVER_PYTHON)

if not SERVER_PYTHON.exists():
    SERVER_PYTHON = Path(sys.executable)

print("Server file:", SERVER_FILE)
print("Server Python:", SERVER_PYTHON)
print("Server file exists:", SERVER_FILE.exists())
print("Python exists:", SERVER_PYTHON.exists())

SERVER_PARAMETERS = StdioServerParameters(
    command=str(SERVER_PYTHON),
    args=[str(SERVER_FILE)],
    env=os.environ.copy(),
)




async def get_mcp_tools_metadata() -> list[dict[str, str]]:
    """Discover tool names and descriptions from the MCP server."""
    async with stdio_client(SERVER_PARAMETERS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.list_tools()

            return [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                }
                for tool in response.tools
            ]


async def get_mcp_tool_schemas() -> list[dict[str, Any]]:
    """Return tool metadata and JSON input schemas."""
    async with stdio_client(SERVER_PARAMETERS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.list_tools()

            return [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                }
                for tool in response.tools
            ]


async def execute_mcp_tool(
    name: str,
    args: dict[str, Any] | None = None,
) -> tuple[str, bool, list[dict[str, Any]]]:
    """Invoke an MCP tool and return text, error status, and restaurants."""
    try:
        async with stdio_client(SERVER_PARAMETERS,errlog=sys.stderr,) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                response = await session.call_tool(
                    name,
                    arguments=args or {},
                )

                content_parts = [
                    item.text
                    for item in response.content
                    if hasattr(item, "text")
                ]

                structured = getattr(
                    response,
                    "structuredContent",
                    None,
                )

                if structured is not None:
                    content_str = json.dumps(
                        structured,
                        ensure_ascii=False,
                        default=str,
                    )
                else:
                    content_str = "\n".join(content_parts)

                if not content_str:
                    content_str = "{}"

                try:
                    parsed = json.loads(content_str)
                except json.JSONDecodeError:
                    parsed = None

                # Supports both a list of restaurants and a single result.
                if isinstance(parsed, list):
                    restaurants = [
                        item for item in parsed
                        if isinstance(item, dict)
                        and "restaurant_id" in item
                    ]
                elif (
                    isinstance(parsed, dict)
                    and "restaurant_id" in parsed
                ):
                    restaurants = [parsed]
                else:
                    restaurants = []

                return (
                    content_str,
                    bool(response.isError),
                    restaurants,
                )

    except Exception as exc:
        return (
            json.dumps({"error": str(exc)}, ensure_ascii=False),
            True,
            [],
        )


if __name__ == "__main__":
    async def main():
        print("Discovering MCP tools...")
        tools = await get_mcp_tools_metadata()

        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")

        print("\nTesting restaurant search...")
        result = await execute_mcp_tool(
            "search_restaurants",
            {
                "city": "Hyderabad",
                "cuisine": "Indian",
                "vegetarian_only": True,
            },
        )

        print("Result:", result[0])
        print("Error:", result[1])

    asyncio.run(main())
