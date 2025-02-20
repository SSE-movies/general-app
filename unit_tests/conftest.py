"""Pytest configuration and shared fixtures for testing."""
import pytest
import uuid
import bcrypt
from src import create_app
from src.database import supabase

@pytest.fixture(scope='module')
def app():
    """Create a Flask app configured for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False
    })
    return app

@pytest.fixture(scope='module')
def client(app):
    """Create a test client for making requests."""
    return app.test_client()

@pytest.fixture(scope='module')
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='module')
def test_user(client):
    """
    Create and return a test user.

    Yields:
        dict: Test user credentials and details
    """
    # Create a test user
    username = "testuser"
    password = "testpass"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    user_data = {
        "username": username,
        "password": hashed_password.decode("utf-8"),
        "is_admin": False,
    }

    # First, clear any related data in other tables
    try:
        # Delete any watchlist entries for this user
        supabase.table("watchlist").delete().eq("username", username).execute()
    except Exception:
        pass  # Ignore if no entries exist

    # Now try to delete the user
    try:
        supabase.table("profiles").delete().eq("username", username).execute()
    except Exception:
        pass  # Ignore if user doesn't exist or can't be deleted

    # Insert the test user
    response = supabase.table("profiles").insert(user_data).execute()
    user = response.data[0] if response.data else None

    yield {
        "username": username,
        "password": password,
        "id": user['id'] if user else None
    }

    # Cleanup: Delete test user and associated data
    try:
        supabase.table("watchlist").delete().eq("username", username).execute()
        supabase.table("profiles").delete().eq("username", username).execute()
    except Exception:
        pass


@pytest.fixture(scope='module')
def test_admin(client):
    """
    Create and return a test admin user.

    Yields:
        dict: Test admin user credentials and details
    """
    # Create a test admin user
    username = "admin"
    password = "adminpass"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    admin_data = {
        "username": username,
        "password": hashed_password.decode("utf-8"),
        "is_admin": True,
    }

    # First, clear any related data in other tables
    try:
        # Delete any watchlist entries for this admin
        supabase.table("watchlist").delete().eq("username", username).execute()
    except Exception:
        pass  # Ignore if no entries exist

    # Now try to delete the admin user
    try:
        supabase.table("profiles").delete().eq("username", username).execute()
    except Exception:
        pass  # Ignore if user doesn't exist or can't be deleted

    # Insert the test admin
    response = supabase.table("profiles").insert(admin_data).execute()
    admin = response.data[0] if response.data else None

    yield {
        "username": username,
        "password": password,
        "id": admin['id'] if admin else None
    }

    # Cleanup: Delete test admin and associated data
    try:
        supabase.table("watchlist").delete().eq("username", username).execute()
        supabase.table("profiles").delete().eq("username", username).execute()
    except Exception:
        pass

@pytest.fixture
def auth_headers(client, test_user):
    """
    Logs in as a test user and returns the test client.

    Args:
        client: Flask test client
        test_user: Fixture providing test user credentials

    Returns:
        FlaskClient: Authenticated test client
    """
    response = client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        }
    )
    assert response.status_code in [200, 302], f"Login failed: {response.status_code}"
    return client

@pytest.fixture
def admin_headers(client, test_admin):
    """
    Logs in as an admin and returns the test client.

    Args:
        client: Flask test client
        test_admin: Fixture providing admin user credentials

    Returns:
        FlaskClient: Authenticated test client
    """
    response = client.post(
        "/login",
        data={
            "username": test_admin["username"],
            "password": test_admin["password"],
        }
    )
    assert response.status_code in [200, 302], f"Admin login failed: {response.status_code}"
    return client

@pytest.fixture
def test_movie(client):
    """
    Create and return a test movie.

    Yields:
        dict: Test movie details
    """
    # Create a test movie
    movie_data = {
        "showId": "test123",
        "title": "Test Movie",
        "listed_in": "Action & Adventure",
        "type": "Movie",
        "description": "Test description"
    }

    # First, delete any existing test movie
    supabase.table("movies").delete().eq("showId", "test123").execute()

    # Insert test movie into database
    response = supabase.table("movies").insert(movie_data).execute()
    movie = response.data[0] if response.data else None

    yield {
        "showId": "test123",
        "title": "Test Movie"
    }

    # Cleanup: Delete test movie
    supabase.table("movies").delete().eq("showId", "test123").execute()