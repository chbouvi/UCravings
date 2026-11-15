"""Compare matching rules against the manually reviewed food pairs."""

import csv
import re
from pathlib import Path


def last_word(name):
    words = re.findall(r"[a-z]+", name.casefold())
    return words[-1] if words else ""


csv_path = Path(__file__).with_name("pair_labels.csv")
with csv_path.open(newline="", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

for rule_name, check_last_word in [
    ("Cosine only", False),
    ("Cosine + last word", True),
]:
    good_suggestions = 0
    bad_suggestions = 0
    missed_good_matches = 0

    for row in rows:
        if row["good_match"] not in ("0", "1"):
            continue  # Unreviewed pairs should not count as bad matches.

        suggested = float(row["cosine_score"]) >= 0.65
        if check_last_word:
            suggested = suggested and (
                last_word(row["favorite"]) == last_word(row["candidate"])
            )

        is_good = row["good_match"] == "1"
        if suggested and is_good:
            good_suggestions += 1
        elif suggested and not is_good:
            bad_suggestions += 1
        elif not suggested and is_good:
            missed_good_matches += 1

    print(rule_name)
    print("  Good suggestions:", good_suggestions)
    print("  Bad suggestions:", bad_suggestions)
    print("  Missed good matches:", missed_good_matches)
