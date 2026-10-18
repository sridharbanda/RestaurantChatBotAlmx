import json
from pathlib import Path
from langchain_core.tools import tool

DATA = Path(__file__).parent / "data" / "restaurants.json"
def restaurants():
    return json.loads(DATA.read_text(encoding="utf-8"))

@tool
def search_restaurants(cuisine: str = "", location: str = "", max_price: int = 0, vegetarian: bool = False) -> list[dict]:
    """Search sample restaurants by cuisine, city, maximum price level 1-3, and vegetarian preference."""
    rows = restaurants()
    if cuisine: rows = [r for r in rows if cuisine.lower() in r["cuisine"].lower()]
    if location: rows = [r for r in rows if location.lower() in r["location"].lower()]
    if max_price: rows = [r for r in rows if r["price_range"] <= max_price]
    if vegetarian: rows = [r for r in rows if r["vegetarian"]]
    return [{k:v for k,v in r.items() if k != "contact"} for r in rows]

@tool
def get_restaurant_details(restaurant_id: str) -> dict:
    """Get restaurant details using an ID such as R001."""
    r = next((r for r in restaurants() if r["restaurant_id"].lower() == restaurant_id.lower()), None)
    return {k:v for k,v in r.items() if k != "contact"} if r else {"error":"Restaurant not found"}

@tool
def get_restaurant_menu(restaurant_id: str) -> dict:
    """Get menu items and prices for a restaurant ID."""
    r = next((r for r in restaurants() if r["restaurant_id"].lower() == restaurant_id.lower()), None)
    return {"name":r["name"],"restaurant_id":r["restaurant_id"],"menu":r["menu"]} if r else {"error":"Restaurant not found"}

@tool
def find_vegetarian_restaurants(location: str = "", cuisine: str = "") -> list[dict]:
    """Find vegetarian restaurants by optional city and cuisine."""
    return search_restaurants.invoke({"location":location,"cuisine":cuisine,"vegetarian":True})

@tool
def filter_restaurants_by_rating(min_rating: float = 4.0, location: str = "") -> list[dict]:
    """Find restaurants rated at least min_rating, optionally in a city."""
    rows = [r for r in restaurants() if r["rating"] >= min_rating and (not location or location.lower() in r["location"].lower())]
    return [{k:v for k,v in r.items() if k != "contact"} for r in rows]

@tool
def recommend_restaurants(cuisine: str = "", budget: int = 0, preferred_location: str = "", vegetarian: bool = False, min_rating: float = 0.0) -> list[dict]:
    """Recommend top restaurants using cuisine, budget level 1-3, city, vegetarian preference, and minimum rating."""
    rows = search_restaurants.invoke({"cuisine":cuisine,"location":preferred_location,"max_price":budget,"vegetarian":vegetarian})
    rows = [r for r in rows if r["rating"] >= min_rating]
    return sorted(rows,key=lambda r:r["rating"],reverse=True)[:5]

@tool
def compare_restaurants(restaurant_ids: list[str]) -> list[dict]:
    """Compare restaurants by IDs; returns only matching restaurants."""
    rows = restaurants()
    return [{k:r[k] for k in ("restaurant_id","name","cuisine","location","rating","price_range","vegetarian")}
            for rid in restaurant_ids for r in rows if r["restaurant_id"].lower() == rid.lower()]

@tool
def get_restaurant_contact(restaurant_id: str) -> dict:
    """Get sample phone number and address for a restaurant ID."""
    r = next((r for r in restaurants() if r["restaurant_id"].lower() == restaurant_id.lower()), None)
    return {"name":r["name"],"contact":r["contact"],"address":r["address"]} if r else {"error":"Restaurant not found"}

TOOLS = [search_restaurants,get_restaurant_details,get_restaurant_menu,find_vegetarian_restaurants,
         filter_restaurants_by_rating,recommend_restaurants,compare_restaurants,get_restaurant_contact]
