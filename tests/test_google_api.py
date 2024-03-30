import pytest
import requests_mock

from ficamp.classifier.google_apis import (
    find_business_category_in_google,
    get_place_details,
    query_google_places_new,
    search_google_maps,
)


@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m


def test_search_google_maps(mock_requests):
    mock_response = {
        "results": [{"types": ["restaurant", "food"], "place_id": "some_place_id"}]
    }
    mock_requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        json=mock_response,
        status_code=200,
    )

    place_id, categories = search_google_maps("Pizza", "52.3676,4.9041")
    assert place_id == "some_place_id"
    assert "restaurant" in categories

def test_search_google_maps_request_failure(mock_requests):
    mock_requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json", status_code=404)

    place_id, categories = search_google_maps('Pizza', '52.3676,4.9041')
    assert place_id is None
    assert categories is None



def test_get_place_details(mock_requests):
    mock_response = {"types": ["bar", "night_club"]}
    mock_requests.get(
        "https://places.googleapis.com/v1/places/some_place_id",
        json=mock_response,
        status_code=200,
    )

    categories = get_place_details("some_place_id")
    assert "bar" in categories


def test_query_google_places_new(mock_requests):
    mock_response = {
        "places": [{"types": ["cafe", "food"], "place_id": "new_place_id"}]
    }
    mock_requests.post(
        "https://places.googleapis.com/v1/places:searchText",
        json=mock_response,
        status_code=200,
    )

    place_id, categories = query_google_places_new("Coffee")
    assert place_id == "new_place_id"
    assert "cafe" in categories


def test_find_business_category_in_google(mock_requests):
    # This test can be more complex due to the nature of the function
    # Implement detailed testing logic here using mock_requests for different scenarios
    pass
