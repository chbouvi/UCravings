# Food Finder

Student project for exploring UMass Amherst dining commons menus and finding favorite foods.

## Run the frontend

From this repository folder:

```bash
python3 -m http.server 8000
```

Open http://127.0.0.1:8000/. Stop the server with Ctrl+C. No frontend packages are needed.

The page reads the repository's `menus.json` and lets you browse its saved menu snapshot by dining hall and meal. It displays the file's saved date but does not claim the menu is currently being served. Favorites are stored in browser Local Storage under `foodfinder-favorites-v2` and can be added or removed on the page.

## Backend handoff

The frontend does not compute food matches. Clicking **Find food** sends a JSON request to `POST /api/search`:

```json
{ "favorites": ["Black Bean Burger", "Cheesecake"], "meal": "Lunch" }
```

It expects a JSON response shaped like:

```json
{
  "matches": [
    {
      "name": "Black Bean Burger",
      "hall": "Berkshire",
      "meal": "Lunch",
      "station": "Grill Station",
      "matched_favorite": "Black Bean Burger",
      "match_type": "Exact",
      "source_url": "https://www.umassdining.com/locations-menus/berkshire/menu"
    }
  ]
}
```

`name`, `hall`, and `meal` are the minimum fields the result card displays. The other fields are optional. The example shows the interface shape; it is not a live menu claim. Until you implement an HTTP endpoint, the page says search is not connected. `scraper.py` and `search.py` are your team's backend work and are not called by this static page.
