"""
Logic to categorize transactions based on keywords.
"""
import json
import pathlib


# path = "./src/ficamp/classifier/keywords.json"
# categories = json.loads(pathlib.Path(path).read_text())


def sort_by_keyword_matches(categories: dict, description):
    description = description.lower()
    matches = []
    for category, keywords in categories.items():
        n_matches = sum(keyword in description for keyword in keywords)
        matches.append((n_matches, category))
    return sorted(matches, reverse=True)
