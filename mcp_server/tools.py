
RESTAURANTS = [
    {
        "restaurant_id": "R001",
        "name": "Green Leaf",
        "city": "Hyderabad",
        "cuisine": "Indian",
        "vegetarian": True,
        "rating": 4.5,
        "reviews": 320,
        "menu": ["Paneer Biryani", "Masala Dosa", "Veg Thali"],
    },
    {
        "restaurant_id": "R002",
        "name": "Pasta House",
        "city": "Hyderabad",
        "cuisine": "Italian",
        "vegetarian": True,
        "rating": 4.3,
        "reviews": 210,
        "menu": ["Margherita Pizza", "Penne Alfredo"],
    },
    {
        "restaurant_id": "R003",
        "name": "Spice Hub",
        "city": "Hyderabad",
        "cuisine": "Indian",
        "vegetarian": False,
        "rating": 4.1,
        "reviews": 180,
        "menu": ["Chicken Biryani", "Chicken Tikka"],
    },
]


def search_restaurants(
    city: str,
    cuisine: str = "",
    vegetarian_only: bool = False,
) -> list[dict]:
    """Search restaurants by city, cuisine and dietary preference."""
    results = []

    for restaurant in RESTAURANTS:
        if restaurant["city"].casefold() != city.casefold():
            continue

        if cuisine and cuisine.casefold() not in restaurant["cuisine"].casefold():
            continue

        if vegetarian_only and not restaurant["vegetarian"]:
            continue

        results.append({
            key: value
            for key, value in restaurant.items()
            if key != "menu"
        })

    return results


def get_restaurant_menu(name: str) -> dict:
    """Return the menu of a restaurant."""
    for restaurant in RESTAURANTS:
        if restaurant["name"].casefold() == name.casefold():
            return {
                "restaurant_id": restaurant["restaurant_id"],
                "name": restaurant["name"],
                "menu": restaurant["menu"],
            }

    return {"error": f"Restaurant not found: {name}"}


def get_restaurant_rating(name: str) -> dict:
    """Return a restaurant's rating and number of reviews."""
    for restaurant in RESTAURANTS:
        if restaurant["name"].casefold() == name.casefold():
            return {
                "restaurant_id": restaurant["restaurant_id"],
                "name": restaurant["name"],
                "rating": restaurant["rating"],
                "reviews": restaurant["reviews"],
            }

    return {"error": f"Restaurant not found: {name}"}


def compare_restaurants(names: list[str]) -> list[dict]:
    """Compare restaurants by rating, cuisine and review count."""
    results = []

    for name in names:
        restaurant = next(
            (
                item for item in RESTAURANTS
                if item["name"].casefold() == name.casefold()
            ),
            None,
        )

        if restaurant:
            results.append({
                "restaurant_id": restaurant["restaurant_id"],
                "name": restaurant["name"],
                "cuisine": restaurant["cuisine"],
                "rating": restaurant["rating"],
                "reviews": restaurant["reviews"],
            })

    return results
