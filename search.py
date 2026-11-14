import json

with open("menus.json", "r") as m:
    loaded = json.load(m)

halls = loaded

foods = []

for hall in halls:
    for meal in halls[hall]:
        for item in halls[hall][meal]:
            foods.append({"name": item, "hall": hall, "meal":})


