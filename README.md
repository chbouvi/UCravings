# UCravings

Find foods you like in saved menus from the four UMass Amherst dining commons.

## Run it

In the project folder, set up Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The food similarity model is a separate download. Run this once on each computer while you have internet access:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

Start the site:

```bash
python server.py
```

Open http://127.0.0.1:8000/. Press Ctrl+C to stop it. The server uses the downloaded model without checking the internet. Restart it after changing Python code or updating `menus.json`.

## Menus and favorites

`scraper.py` saves the dining hall menus to `menus.json`. Run `python scraper.py` to refresh the file, then check that it found items for all four halls. The site shows the date of that saved menu; it does not update menus on its own.

Favorites are saved in your browser's Local Storage under `foodfinder-favorites-v2`.

## Search request

Clicking **Find food** sends a request to `POST /api/search`:

```json
{"favorites": ["Veggie Burger"], "meal": "Lunch"}
```

The server returns `{"matches": [...]}`. Each match has a dish name, hall, meal, and either `Exact` or `Similar` as its match type. Similar matches also say which favorite they matched. The site groups repeated dishes by hall and meal before displaying them.
