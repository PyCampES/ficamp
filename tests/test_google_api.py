import pytest
import requests_mock

from ficamp.classifier.google_apis import (
    GoogleException,
    find_business_category_in_google,
    get_place_details,
    query_google_places_new,
    search_google_maps,
)


@pytest.fixture(name="mock_requests")
def mock_requests_fixture():
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
        "https://maps.googleapis.com/maps/api/place/textsearch/json", status_code=404
    )

    place_id, categories = search_google_maps("Pizza", "52.3676,4.9041")
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


def test_get_place_details_request_failure(mock_requests):
    mock_requests.get(
        "https://places.googleapis.com/v1/places/some_place_id", status_code=500
    )

    categories = get_place_details("some_place_id")
    assert categories == []


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


def test_query_google_places_new_request_failure(mock_requests):
    mock_requests.post(
        "https://places.googleapis.com/v1/places:searchText", status_code=503
    )

    place_id, categories = query_google_places_new("Coffee")
    assert place_id is None
    assert categories is None


def test_find_business_category_no_place_id_no_categories(mock_requests):
    # Mock both APIs to return no place_id and no categories
    mock_requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        json={"results": []},
        status_code=200,
    )
    mock_requests.post(
        "https://places.googleapis.com/v1/places:searchText",
        json={"places": []},
        status_code=200,
    )

    # Test function call and assert GoogleException
    with pytest.raises(GoogleException):
        find_business_category_in_google("Some Business")


def test_find_business_category_maps_no_categories_details_fail_new_places_success(
    mock_requests,
):
    # Mock search_google_maps with only place_id and no types
    mock_requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        json={"results": [{"types": [], "place_id": "some_place_id"}]},
        status_code=200,
    )

    # Mock get_place_details to fail
    mock_requests.get(
        "https://places.googleapis.com/v1/places/some_place_id",
        json={"types": []},
        status_code=200,
    )

    # Mock query_google_places_new to succeed
    mock_requests.post(
        "https://places.googleapis.com/v1/places:searchText",
        json={"places": [{"types": ["cafe"], "place_id": "new_place_id"}]},
        status_code=200,
    )

    # Test function call
    category = find_business_category_in_google("Some Business")

    # Assertions
    assert category == "cafe"


def test_find_business_category_new_places_no_categories_details_success(mock_requests):
    # Mock search_google_maps to fail
    mock_requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        json={"results": []},
        status_code=200,
    )

    # Mock query_google_places_new to return place_id but no types
    mock_requests.post(
        "https://places.googleapis.com/v1/places:searchText",
        json={"places": [{"types": [], "place_id": "new_place_id"}]},
        status_code=200,
    )

    # Mock get_place_details to succeed
    mock_requests.get(
        "https://places.googleapis.com/v1/places/new_place_id",
        json={"types": ["bakery"]},
        status_code=200,
    )

    # Test function call
    category = find_business_category_in_google("Some Bakery")

    # Assertions
    assert category == "bakery"


def test_find_business_category_all_filtered_out_raise_exception(mock_requests):
    # Mock APIs to return place_id and filtered categories
    mock_requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        json={
            "results": [{"types": ["point_of_interest"], "place_id": "some_place_id"}]
        },
        status_code=200,
    )
    mock_requests.post(
        "https://places.googleapis.com/v1/places:searchText",
        json={"places": [{"types": ["establishment"], "place_id": "new_place_id"}]},
        status_code=200,
    )

    # Test function call and assert GoogleException
    with pytest.raises(GoogleException):
        find_business_category_in_google("Some Business")
