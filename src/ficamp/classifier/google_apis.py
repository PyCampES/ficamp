import json

import requests

GOOGLE_API_KEY = "FIXME_GET_FROM_ENV"


class GoogleException(Exception):
    """Custom Exception for raising errors to the caller."""


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
    return []


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


def find_business_category_in_google(field, location=None):
    keys_to_remove = ["point_of_interest", "establishment", "store", "department_store"]
    # first try using google map places search
    place_id_gmaps, categories = search_google_maps(field, location)
    if not categories and place_id_gmaps:
        # if we get a place_id but no categories then query the details
        categories = get_place_details(place_id_gmaps)
    if not categories:
        # if still no categories then try with the new API
        place_id_gplaces, categories = query_google_places_new(field)
        if not categories and place_id_gplaces:
            # if we get a place_id but no categories then query the details
            categories = get_place_details(place_id_gplaces)
    if not categories:
        raise GoogleException("Not found in G Maps or G Places")
    categories = list(set(categories) - set(keys_to_remove))
    if categories:
        categories = list(set(categories) - set(keys_to_remove))
        return categories[0]
    raise GoogleException
