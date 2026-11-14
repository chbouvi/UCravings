import json

data = {"berkshire": {"lunch": ["Pizza", "Salad"]}}

with open("test.json", "w") as f:
    json.dump(data, f, indent=4)

with open("test.json", "r") as f:
    loaded = json.load(f)

print(loaded)
print(loaded == data)