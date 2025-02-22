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
    try:
        # First, remove any watchlist entries referencing this movie
        supabase.table("watchlist").delete().eq("showId", movie_id).execute()

        # Then delete the movie
        supabase.table("movies").delete().eq("showId", movie_id).execute()
    except Exception as e:
        print(f"Cleanup error: {e}")


def test_add_to_watchlist(client, auth_headers, test_movie):
    """Test adding a movie to the watchlist."""
    response = client.post(
        "/add_to_watchlist",
        headers=auth_headers,  # Ensure authenticated request
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.get_json()
    assert data["message"] == "Successfully added to watchlist", f"Unexpected message: {data}"



def test_duplicate_watchlist_add(client, auth_headers, test_movie):
    """Ensure adding the same movie twice does not create duplicates."""
    client.post(
        "/add_to_watchlist",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    response = client.post(
        "/add_to_watchlist",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    assert response.status_code == 400, f"Unexpected status code: {response.status_code}"
    data = response.get_json()
    assert "Already in watchlist" in data["message"], f"Unexpected message: {data}"


def test_view_watchlist(client, auth_headers, test_movie):
    """Ensure the user can view their watchlist."""
    client.post(
        "/add_to_watchlist",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    response = client.get("/my_watchlist", headers=auth_headers)  # Added headers

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    data = response.get_json()
    assert any(movie["title"] == test_movie["title"] for movie in data), f"Movie title missing in watchlist: {data}"


def test_remove_from_watchlist(client, auth_headers, test_movie):
    """Ensure movies can be removed from the watchlist."""
    client.post(
        "/add_to_watchlist",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    response = client.post(
        "/remove_from_watchlist",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    # Verify movie is removed
    response = client.get("/my_watchlist", headers=auth_headers)  # Added headers
    data = response.get_json()

    assert not any(movie["title"] == test_movie["title"] for movie in data), f"Movie still in watchlist: {data}"


def test_mark_watched(client, auth_headers, test_movie):
    """Ensure a movie can be marked as watched."""
    client.post(
        "/add_to_watchlist",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    response = client.post(
        "/mark_watched",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"



def test_mark_unwatched(client, auth_headers, test_movie):
    """Ensure a movie can be marked as unwatched."""
    client.post(
        "/add_to_watchlist",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )
    client.post(
        "/mark_watched",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    response = client.post(
        "/mark_unwatched",
        headers=auth_headers,  # Added
        json={"showId": test_movie["showId"]},
        content_type="application/json",
    )

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

