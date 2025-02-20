import json
import pytest

@pytest.fixture
def test_movie():
    # Add a test movie to the database
    movie_data = {
        "showId": "test123",
        "title": "Test Movie",
        "listedIn": "Action & Adventure",
        "type": "Movie",
        "description": "Test description"
    }
    response = supabase.table("movies").insert(movie_data).execute()
    yield response.data[0]
    # Cleanup not needed as we want to keep movies in the database


def test_add_to_watchlist(auth_headers, test_movie):
    response = auth_headers.post("/add_to_watchlist",
                                 json={"showId": test_movie["showId"]})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Successfully added to watchlist"


def test_duplicate_watchlist_add(auth_headers, test_movie):
    # Add movie first time
    auth_headers.post("/add_to_watchlist",
                      json={"showId": test_movie["showId"]})

    # Try to add same movie again
    response = auth_headers.post("/add_to_watchlist",
                                 json={"showId": test_movie["showId"]})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Already in watchlist"


def test_view_watchlist(auth_headers, test_movie):
    # First add a movie to watchlist
    auth_headers.post("/add_to_watchlist",
                      json={"showId": test_movie["showId"]})

    # Then view watchlist
    response = auth_headers.get("/my_watchlist")
    assert response.status_code == 200
    assert bytes(test_movie["title"], 'utf-8') in response.data


def test_remove_from_watchlist(auth_headers, test_movie):
    # First add a movie
    auth_headers.post("/add_to_watchlist",
                      json={"showId": test_movie["showId"]})

    # Then remove it
    response = auth_headers.post("/remove_from_watchlist",
                                 data={"showId": test_movie["showId"]})
    assert response.status_code == 302  # Redirects back to watchlist

    # Verify it's removed
    response = auth_headers.get("/my_watchlist")
    assert bytes(test_movie["title"], 'utf-8') not in response.data

def test_mark_watched(auth_headers, test_movie):
    # Add movie to watchlist
    auth_headers.post("/add_to_watchlist",
                      json={"showId": test_movie["showId"]})

    # Mark as watched
    response = auth_headers.post("/mark_watched",
                                 data={"showId": test_movie["showId"]})
    assert response.status_code == 302


def test_mark_unwatched(auth_headers, test_movie):
    # Add movie and mark as watched first
    auth_headers.post("/add_to_watchlist",
                      json={"showId": test_movie["showId"]})
    auth_headers.post("/mark_watched",
                      data={"showId": test_movie["showId"]})

    # Then mark as unwatched
    response = auth_headers.post("/mark_unwatched",
                                 data={"showId": test_movie["showId"]})
    assert response.status_code == 302