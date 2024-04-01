"""
Logic to sort transactions based on keywords.
"""
import json
import pathlib


def sort_by_keyword_matches(categories: dict, description: str) -> list[str]:
    description = description.lower()
    matches = []
    for category, keywords in categories.items():
        n_matches = sum(keyword in description for keyword in keywords)
        matches.append((n_matches, category))
    return sorted(matches, reverse=True)
