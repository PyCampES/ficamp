from ficamp.classifier.google_apis import query_gmaps_category


def infer_tx_category(tx):
    """Will try to guess the category using different actions."""
    print(f"Raw is: {tx.concept}\n")
    gmap_category = query_gmaps_category(tx.concept_clean)
    if gmap_category:
        print(f"Google Maps category is {gmap_category}")
    return gmap_category
