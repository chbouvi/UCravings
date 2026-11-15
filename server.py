from flask import Flask, send_from_directory, request
from search import load_foods
from semantic_explore import find_similar

app = Flask(__name__)


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.get("/<filename>")
def frontend_file(filename):
    if filename not in {"index.html", "app.js", "styles.css", "menus.json", "food-background.png", "library.svg"}:
        return "Not found", 404
    return send_from_directory(app.root_path, filename)


@app.post("/api/search")
def search_api():
    data = request.get_json() or {}
    favorite_names = data.get("favorites", [])
    favorites = {name.strip().casefold() for name in favorite_names}
    meal = data.get("meal", "All meals")
    meal_keys = {
        "All meals": None,
        "Breakfast": "breakfast",
        "Lunch": "lunch",
        "Dinner": "dinner",
        "Late Night": "latenight",
    }
    selected_meal = meal_keys[meal]

    matches = []
    for food in load_foods():
        if food["name"].casefold() not in favorites:
            continue
        if selected_meal is not None and food["meal"] != selected_meal:
            continue

        result = food.copy()
        result["match_type"] = "Exact"
        matches.append(result)

    for favorite in favorite_names:
        matches.extend(find_similar(favorite, meal))
    
    return {"matches": matches}

if __name__ == "__main__":
    app.run(port=8000, debug=True, use_reloader=False)
