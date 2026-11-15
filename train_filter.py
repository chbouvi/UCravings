import re
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
import csv
from pathlib import Path


def score(row) -> list[float]:
    favorite_words = re.findall(r"[a-z]+", row["favorite"].casefold())
    candidate_words = re.findall(r"[a-z]+", row["candidate"].casefold())

    cosine = float(row["cosine_score"])
    same_last_word = float(favorite_words[-1] == candidate_words[-1])

    favorite_set = set(favorite_words)
    candidate_set = set(candidate_words)
    shared_fraction = len(favorite_set & candidate_set) / len(favorite_set | candidate_set)

    return [cosine, same_last_word, shared_fraction]

X = []
y = []
groups = []

csv_path = Path(__file__).with_name("pair_labels.csv")
with csv_path.open(newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        if row["good_match"] not in ("0", "1"):
            continue
        X.append(score(row))
        y.append(int(row["good_match"]))
        groups.append(row["favorite"])

print("Rows:", len(X), "Good matches:", sum(y))
print("First row:", X[0], y[0], groups[0])

splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=0)
train_ids, test_ids = next(splitter.split(X, y, groups))

X_train = [X[i] for i in train_ids]
y_train = [y[i] for i in train_ids]
X_test = [X[i] for i in test_ids]

model = LogisticRegression(class_weight="balanced")
model.fit(X_train, y_train)

predictions = model.predict(X_test)
print("Predicted good matches:", sum(predictions))
print("Actually good matches:", sum(y[i] for i in test_ids))

good_suggestions = 0
bad_suggestions = 0
missed_good_matches = 0

for position, row_id in enumerate(test_ids):
    predicted_good = predictions[position] == 1
    actually_good = y[row_id] == 1

    if predicted_good and actually_good:
        good_suggestions += 1
    elif predicted_good and not actually_good:
        bad_suggestions += 1
    elif not predicted_good and actually_good:
        missed_good_matches += 1

print("Good suggestions:", good_suggestions)
print("Bad suggestions:", bad_suggestions)
print("Missed good matches:", missed_good_matches)

for use_last_word in (False, True):
    good = bad = missed = 0

    for row_id in test_ids:
        predicted_good = X[row_id][0] >= 0.65  # First number: cosine
        if use_last_word:
            predicted_good = predicted_good and X[row_id][1] == 1.0

        actually_good = y[row_id] == 1
        if predicted_good and actually_good:
            good += 1
        elif predicted_good and not actually_good:
            bad += 1
        elif not predicted_good and actually_good:
            missed += 1

    print("Use last word:", use_last_word, "Good:", good, "Bad:", bad, "Missed:", missed)