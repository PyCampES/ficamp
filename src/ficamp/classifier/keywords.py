"""
Logic to sort transactions based on keywords.
"""

from typing import Any


def sort_by_keyword_matches(
    categories: dict, description: str
) -> list[tuple[int, Any]]:
    description = description.lower()
    matches = []
    for category, keywords in categories.items():
        n_matches = sum(keyword in description for keyword in keywords)
        matches.append((n_matches, category))
    return sorted(matches, reverse=True)
