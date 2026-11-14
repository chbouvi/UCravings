import requests
from bs4 import BeautifulSoup
import json
from datetime import date

dining_halls = ["https://www.umassdining.com/locations-menus/berkshire/menu",
"https://www.umassdining.com/locations-menus/worcester/menu",
"https://www.umassdining.com/locations-menus/hampshire/menu",
"https://www.umassdining.com/locations-menus/franklin/menu"]

current_menu = {}


for hall in dining_halls:
    meals = {}
    response = requests.get(hall)
    soup = BeautifulSoup(response.text, "html.parser")

    breakfast = soup.find("div", id="breakfast_menu")
    if breakfast is not None:
        breakfast_items = breakfast.find_all("a", attrs={"data-healthfulness": True})
        breakfast_menu = []
        for item in breakfast_items:
            breakfast_menu.append(item.get_text(strip=True))
        meals["breakfast"]=breakfast_menu

    lunch = soup.find("div", id="lunch_menu")
    if lunch is not None:
        lunch_items = lunch.find_all("a", attrs={"data-healthfulness": True})
        lunch_menu = []
        for item in lunch_items:
            lunch_menu.append(item.get_text(strip=True))
        meals["lunch"]=lunch_menu

    dinner = soup.find("div", id="dinner_menu")
    if dinner is not None:
        dinner_items = dinner.find_all("a", attrs={"data-healthfulness": True})
        dinner_menu = []
        for item in dinner_items:
            dinner_menu.append(item.get_text(strip=True))
        meals["dinner"]=dinner_menu

    latenight = soup.find("div", id="latenight_menu")
    if latenight is not None:
        latenight_items = latenight.find_all("a", attrs={"data-healthfulness": True})
        latenight_menu = []
        for item in latenight_items:
            latenight_menu.append(item.get_text(strip=True))
        meals["latenight"]=latenight_menu

    parts = hall.split("/")
    current_menu[parts[4]]=meals

for hall in current_menu:
    for meal in current_menu[hall]:
        print(hall, meal, ":", len(current_menu[hall][meal]))

saved = {"date": date.today().isoformat(), "halls": current_menu}

with open("menus.json", "w") as m:
    json.dump(saved, m, indent=4)
with open("menus.json", "r") as m:
    loaded = json.load(m)




