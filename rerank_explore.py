from sentence_transformers import CrossEncoder

pairs = [
    ("Veggie Burger", "Black Bean Burger"),
    ("Black Bean Burger", "Black Beans"),
    ("Cheesecake", "Cheese Pizza"),
    ("Cheesecake", "New York Style Cheesecake"),
]

model = CrossEncoder("cross-encoder/stsb-distilroberta-base")
scores = model.predict(pairs)

for pair, score in zip(pairs, scores):
    print(pair, float(score))