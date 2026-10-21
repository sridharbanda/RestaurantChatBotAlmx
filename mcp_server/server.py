
from mcp.server.fastmcp import FastMCP

from tools import (
    search_restaurants as search_restaurants_impl,
    get_restaurant_menu as get_restaurant_menu_impl,
    get_restaurant_rating as get_restaurant_rating_impl,
    compare_restaurants as compare_restaurants_impl,
)

mcp = FastMCP("TableTalk Restaurant Server")


@mcp.tool()
def search_restaurants(
    city: str,
    cuisine: str = "",
    vegetarian_only: bool = False,
) -> list[dict]:
    """Find restaurants by city, cuisine, and vegetarian preference."""
    return search_restaurants_impl(city, cuisine, vegetarian_only)


@mcp.tool()
def get_restaurant_menu(name: str) -> dict:
    """Get the menu for a restaurant by name."""
    return get_restaurant_menu_impl(name)


@mcp.tool()
def get_restaurant_rating(name: str) -> dict:
    """Get a restaurant's rating and review count."""
    return get_restaurant_rating_impl(name)


@mcp.tool()
def compare_restaurants(names: list[str]) -> list[dict]:
    """Compare the ratings and cuisines of multiple restaurants."""
    return compare_restaurants_impl(names)


if __name__ == "__main__":
    # Keep stdout reserved for MCP protocol messages.
    mcp.run(transport="stdio")
