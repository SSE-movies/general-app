import pytest
import uuid
from src.database import supabase

@pytest.fixture
def test_movie():
    """Fixture to create a test movie data (simulating one from Azure API)."""
    return {
        "showId": "s1234",  # Using a known ID from Azure API
        "title": "Test Movie",
        "listedIn": "Action & Adventure",
        "type": "Movie",
        "description": "Test description"
    }

def test_add_to_watchlist(auth_client, test_movie):
    """Test adding a movie to the watchlist."""
    response = auth_client.post(
        "/add_to_watchlist",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )
    assert response.status_code == 200

def test_duplicate_watchlist_add(auth_client, test_movie):
    """Ensure adding the same movie twice works (idempotent)."""
    # First addition
    auth_client.post(
        "/add_to_watchlist",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )

    # Second addition should still succeed
    response = auth_client.post(
        "/add_to_watchlist",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )
    assert response.status_code == 200

def test_view_watchlist(auth_client, test_movie):
    """Ensure the user can view their watchlist."""
    # First add to watchlist
    auth_client.post(
        "/add_to_watchlist",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )

    response = auth_client.get("/my_watchlist")
    assert response.status_code == 200

def test_mark_watched(auth_client, test_movie):
    """Test marking a movie as watched."""
    # Add to watchlist first
    auth_client.post(
        "/add_to_watchlist",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )

    response = auth_client.post(
        "/mark_watched",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )
    assert response.status_code == 200

def test_mark_unwatched(auth_client, test_movie):
    """Test marking a movie as unwatched."""
    # Add to watchlist and mark as watched first
    auth_client.post(
        "/add_to_watchlist",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )
    auth_client.post(
        "/mark_watched",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )

    response = auth_client.post(
        "/mark_unwatched",
        data={"showId": test_movie["showId"]},
        follow_redirects=True
    )
    assert response.status_code == 200

# Add cleanup fixture to remove test entries from watchlist
@pytest.fixture(autouse=True)
def cleanup_watchlist(test_movie):
    yield
    try:
        supabase.table("watchlist").delete().eq("showId", test_movie["showId"]).execute()
    except Exception as e:
        print(f"Cleanup error: {e}")