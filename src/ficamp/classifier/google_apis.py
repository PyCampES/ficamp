import json

import requests

GOOGLE_API_KEY = "FIXME_GET_FROM_ENV"


def search_google_maps(business_name, location=None, api_key=GOOGLE_API_KEY):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": business_name, "key": api_key}
    if location:
        params["location"] = location
        params["radius"] = 5000  # Radius in meters (you can adjust this)

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            # Assuming the first result is the most relevant
            categories = results[0].get("types", [])
            place_id = results[0].get("place_id", None)
            return place_id, categories
    return None, None


def get_place_details(place_id):
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "id,displayName,types",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("types", [])


def query_google_places_new(query):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.name,places.types,places.formattedAddress",
    }
    payload = {"textQuery": query}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        places = response.json().get("places", [])
        if places:
            categories = places[0].get("types", [])
            place_id = places[0].get("place_id", None)
            return place_id, categories
    return None, None


def find_business_category_in_google(field):
    keys_to_remove = ["point_of_interest", "establishment", "store", "department_store"]
    location = "52.3676,4.9041"  # Latitude and longitude of Amsterdam
    # first try using google map places search
    place_id, categories = search_google_maps(field, location)
    if not place_id:
        # try with the new API
        place_id, categories = query_google_places_new(field)
        if not categories and not place_id:
            return "Not found"
    categories = list(set(categories) - set(keys_to_remove))
    if not categories:
        # try to get it from the place details
        categories = get_place_details(place_id)
        if categories:
            categories = list(set(categories) - set(keys_to_remove))
    if categories:
        return categories[0]
    return "Not found"
