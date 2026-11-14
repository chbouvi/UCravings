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

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
vectors = model.encode(names, convert_to_tensor=True)

query = "Veggie Burger"
query_vector = model.encode([query], convert_to_tensor=True)
scores = util.cos_sim(query_vector, vectors)[0]

ranked = sorted(
    zip(names, scores.tolist()),
    key=lambda pair: pair[1],
    reverse=True,
)

for name, score in ranked[:10]:
    locations = [record for record in records if record["name"] == name]
    print(name, score)
    for location in locations:
        print(location["hall"], location["meal"])
