from search import load_foods, search

foods = load_foods()
results = search("chicken", foods)
print(len(results))
print(results[:3])