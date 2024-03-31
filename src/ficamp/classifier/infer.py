from ficamp.classifier.google_apis import query_gmaps_category


def infer_tx_category(tx):
    """Will try to guess the category using different actions."""
    gmap_category = query_gmaps_category(tx.concept)
    if gmap_category != "Unknown":
        print(f"Google Maps category is {gmap_category}")
    return gmap_category
