import pytest
import uuid
import bcrypt
import os
from src import create_app
from src.database import supabase  # Import Supabase client


@pytest.fixture(scope="module")
def app():
    """Create and configure a new app instance for each test module."""
    # Set required environment variables for testing
    os.environ["MOVIES_API_URL"] = (
        "http://sse-movies-project2.emdke0g3fbhkfrgy.uksouth.azurecontainer.io/movies"
    )
    os.environ["SUPABASE_URL"] = "https://euibanwordbygkxadvrx.supabase.co"
    os.environ["SUPABASE_KEY"] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1aWJhbndvcmRieWdreGFkdnJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkzNjM2NDcsImV4cCI6MjA1NDkzOTY0N30.E5AeoS2-6vCHnt1PqsGAtMnaBB8xR48D8XhJ4jvwoEk"
    )

    app = create_app(testing=True)
    app.config["SECRET_KEY"] = "test_secret_key"
    yield app


@pytest.fixture(scope="module")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="module")
def test_user():
    """Create a test user for authentication tests."""
    username = f"testuser_{uuid.uuid4()}"
    password = "password123"

    # Hash the password before storing
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode(
        "utf-8"
    )

    # Check if user exists first
    existing_user = (
        supabase.table("profiles")
        .select("*")
        .eq("username", username)
        .execute()
    )

    if not existing_user.data:
        # Create new user only if doesn't exist
        supabase.table("profiles").insert(
            {
                "username": username,
                "password": hashed_password,
                "is_admin": False,  # Ensure we never create test admin users
            }
        ).execute()

    yield {"username": username, "password": password}


@pytest.fixture(scope="module")
def test_admin():
    """Create an admin user in Supabase with a UUID."""
    # Hash the password
    password = "adminpass123"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    admin_data = {
        "id": str(uuid.uuid4()),
        "username": f"adminuser_{uuid.uuid4()}",  # Unique username for admin
        "is_admin": True,
        "password": hashed_password.decode("utf-8"),  # Store hashed password
    }
    response = supabase.table("profiles").insert(admin_data).execute()

    if response.data:
        # Return admin data with plain password for testing
        return {
            "id": admin_data["id"],
            "username": admin_data["username"],
            "is_admin": admin_data["is_admin"],
            "password": password,  # Return original password for login
        }
    else:
        pytest.fail(f"Failed to create test admin: {response.error}")


@pytest.fixture(scope="module")
def auth_client(client, test_user):
    """Return an authenticated client for a regular user."""
    with client.session_transaction() as sess:
        # Login as test user
        response = client.post(
            "/login",  # Changed from /auth/login
            data={
                "username": test_user["username"],
                "password": test_user["password"],
            },
            follow_redirects=True,
        )

        if response.status_code != 200:
            pytest.fail(
                f"Failed to authenticate test user. Status code: {response.status_code}, Response: {response.data}"
            )

    return client


@pytest.fixture(scope="module")
def admin_client(client, test_admin):
    """Return an authenticated client for an admin user."""
    with client.session_transaction() as sess:
        # Login as admin
        response = client.post(
            "/auth/login",
            data={  # Use form data instead of JSON
                "username": test_admin["username"],
                "password": test_admin["password"],
            },
            follow_redirects=True,
        )

        if response.status_code != 200:
            pytest.fail("Failed to authenticate admin user")

    return client  # Return the client with active session


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup(test_user, test_admin):
    yield
    # Delete test users from database after tests
    supabase.table("profiles").delete().eq(
        "username", test_user["username"]
    ).execute()
    supabase.table("profiles").delete().eq(
        "username", test_admin["username"]
    ).execute()


@pytest.fixture
def test_movie():
    """Fixture to create a test movie entry."""
    movie_id = str(uuid.uuid4())
    movie_data = {
        "showId": movie_id,
        "title": "Test Movie",
        "listedIn": "Action & Adventure",
        "type": "Movie",
        "description": "Test description",
        "release_year": 2024,
        "duration": "90 min",
        "rating": "TV-14",
    }

    yield movie_data

    # Cleanup - remove from watchlist after test
    try:
        supabase.table("watchlist").delete().eq("showId", movie_id).execute()
    except Exception as e:
        print(f"Cleanup error: {e}")
