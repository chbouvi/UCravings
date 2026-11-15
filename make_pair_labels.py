"""Create food-pair examples for a person to label."""

import csv
from pathlib import Path

from sentence_transformers import util

from semantic_explore import model, names, vectors


FAVORITES = [
    "Veggie Burger",
    "Black Bean Burger",
    "Cheesecake",
    "Chicken Parmesan",
    "Cheese Pizza",
    "Tomato Soup",
    "Caesar Salad",
    "Mac and Cheese",
    "Grilled Salmon",
    "Fried Rice",
    "Chocolate Cake",
    "Tacos",
]

output_path = Path(__file__).with_name("pair_labels.csv")
if output_path.exists():
    raise SystemExit("pair_labels.csv already exists; refusing to erase your labels.")

with output_path.open("w", newline="", encoding="utf-8") as output_file:
    writer = csv.writer(output_file)
    writer.writerow(["favorite", "candidate", "cosine_score", "good_match"])

    for favorite in FAVORITES:
        favorite_vector = model.encode([favorite], convert_to_tensor=True)
        scores = util.cos_sim(favorite_vector, vectors)[0].tolist()
        ranked = sorted(zip(names, scores), key=lambda pair: pair[1], reverse=True)

        candidates_written = 0
        for candidate, score in ranked:
            if candidate.casefold() == favorite.casefold():
                continue  # Exact matches do not need similarity judging.
            writer.writerow([favorite, candidate, round(score, 3), ""])
            candidates_written += 1
            if candidates_written == 10:
                break

print(f"Wrote {output_path} with {len(FAVORITES) * 10} pairs to label.")
