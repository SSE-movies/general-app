import json
import pytest
import uuid
from src.database import supabase


@pytest.fixture
def test_movie():
    """Fixture to create a test movie entry in the database."""
    movie_id = str(uuid.uuid4())

    movie_data = {
        "showId": movie_id,
        "title": "Test Movie",
        "listedIn": "Action & Adventure",
        "type": "Movie",
        "description": "Test description",
    }
    response = supabase.table("movies").insert(movie_data).execute()

    yield response.data[0]  # Provide the created movie to the test

    # Cleanup after test
    supabase.table("movies").delete().eq("showId", movie_id).execute()


def test_add_to_watchlist(auth_headers, test_movie):
    """Test adding a movie to the watchlist."""
    response = auth_headers.post(
        "/add_to_watchlist", json={"showId": test_movie["showId"]}
    )
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    data = json.loads(response.data)
    assert (
        data["message"] == "Successfully added to watchlist"
    ), f"Unexpected message: {data}"


def test_duplicate_watchlist_add(auth_headers, test_movie):
    """Ensure adding the same movie twice does not create duplicates."""
    auth_headers.post(
        "/add_to_watchlist", json={"showId": test_movie["showId"]}
    )

    response = auth_headers.post(
        "/add_to_watchlist", json={"showId": test_movie["showId"]}
    )
    assert (
        response.status_code == 400
    ), f"Unexpected status code: {response.status_code}"
    data = json.loads(response.data)
    assert (
        "Already in watchlist" in data["message"]
    ), f"Unexpected message: {data}"


def test_view_watchlist(auth_headers, test_movie):
    """Ensure the user can view their watchlist."""
    auth_headers.post(
        "/add_to_watchlist", json={"showId": test_movie["showId"]}
    )

    response = auth_headers.get("/my_watchlist")
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    assert (
        bytes(test_movie["title"], "utf-8") in response.data
    ), f"Movie title missing in watchlist: {response.data}"


def test_remove_from_watchlist(auth_headers, test_movie):
    """Ensure movies can be removed from the watchlist."""
    auth_headers.post(
        "/add_to_watchlist", json={"showId": test_movie["showId"]}
    )

    response = auth_headers.post(
        "/remove_from_watchlist", json={"showId": test_movie["showId"]}
    )
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"

    # Verify movie is removed
    response = auth_headers.get("/my_watchlist")
    assert (
        bytes(test_movie["title"], "utf-8") not in response.data
    ), f"Movie still in watchlist: {response.data}"


def test_mark_watched(auth_headers, test_movie):
    """Ensure a movie can be marked as watched."""
    auth_headers.post(
        "/add_to_watchlist", json={"showId": test_movie["showId"]}
    )

    response = auth_headers.post(
        "/mark_watched", json={"showId": test_movie["showId"]}
    )
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"


def test_mark_unwatched(auth_headers, test_movie):
    """Ensure a movie can be marked as unwatched."""
    auth_headers.post(
        "/add_to_watchlist", json={"showId": test_movie["showId"]}
    )
    auth_headers.post("/mark_watched", json={"showId": test_movie["showId"]})

    response = auth_headers.post(
        "/mark_unwatched", json={"showId": test_movie["showId"]}
    )
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
