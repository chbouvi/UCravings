from sentence_transformers import SentenceTransformer, util
from pathlib import Path
import json

data = json.loads(
    Path(__file__).with_name("menus.json").read_text(encoding="utf-8")
)
menus = data["halls"]

names = sorted({
    name
    for meals in menus.values()
    for dishes in meals.values()
    for name in dishes
})

records = [
    {"name": name, "hall": hall, "meal": meal}
    for hall, meals in menus.items()
    for meal, dishes in meals.items()
    for name in dishes
]

try:
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2", local_files_only=True
    )
except OSError:
    raise RuntimeError(
        "The food similarity model needs to be downloaded once. "
        "Follow the model step in README.md, then try again."
    ) from None
vectors = model.encode(names, convert_to_tensor=True)

def find_similar(query, meal) -> list[dict]:
    query_vector = model.encode([query], convert_to_tensor=True)
    scores = util.cos_sim(query_vector, vectors)[0]

    meal_keys = {
        "All meals": None,
        "Breakfast": "breakfast",
        "Lunch": "lunch",
        "Dinner": "dinner",
        "Late Night": "latenight",
    }
    selected_meal = meal_keys[meal]

    eligible_names = {
        record["name"]
        for record in records
        if selected_meal is None or record["meal"] == selected_meal
    }

    ranked = sorted(
        ((name, score) for name, score in zip(names, scores.tolist())
        if name in eligible_names),
        key=lambda pair: pair[1],
        reverse=True,
    )

    results = []
    accepted_names = 0
    MIN_SIMILARITY = 0.65

    for name, score in ranked:
        if score < MIN_SIMILARITY:
            break
        if name.strip().casefold() == query.strip().casefold():
            continue
        if "burger" in query.casefold() and "burger" not in name.casefold():
            continue
        locations = [record for record in records if record["name"] == name]
        for location in locations:
            if selected_meal is not None and location["meal"] != selected_meal:
                continue
            result = location.copy()
            result["matched_favorite"] = query
            result["match_type"] = "Similar"
            result["score"] = score
            results.append(result)
        accepted_names += 1
        if accepted_names >= 10:
            break

    return results

if __name__ == "__main__":
    print(find_similar("Veggie Burger", "Lunch")[:2])
    print(find_similar("Black Bean Burger", "Breakfast")[:2])
