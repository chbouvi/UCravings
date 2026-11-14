import json

with open("menus.json", "r") as m:
    loaded = json.load(m)

halls = loaded["halls"]
print(loaded["date"])

foods = []

for hall in halls:
    for meal in halls[hall]:
        for item in halls[hall][meal]:
            foods.append({"name": item, "hall": hall, "meal": meal})

def search(query, foods):
    query = query.lower().strip()
    if query == "":
        return
    found = []
    foodset = set()
    for food in foods:
        if query in food["name"].lower().strip():
            found.append(food)
            foodset.add(food["name"])
    if found == []:
        print("No matches found.")
        return
    for name in sorted(foodset):
        print(name)
        for food in found:
            if food["name"]==name:
                print("\t"+food["hall"][0].upper()+food["hall"][1:]+": "+food["meal"][0].upper()+food["meal"][1:])
        print("")
    return
                

while True:
    query = input("What are you craving? ")
    if query.lower().strip() == "end":
        break
    search(query, foods)







