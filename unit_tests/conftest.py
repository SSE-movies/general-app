import pytest
import uuid
import bcrypt
from src import create_app
from src.database import supabase  # Import Supabase client


@pytest.fixture(scope="module")
def app():
    """Create and configure a new app instance for each test module."""
    app = create_app(testing=True)
    yield app


@pytest.fixture(scope="module")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="module")
def test_user():
    """Create a regular test user in Supabase with a UUID."""
    # Hash the password as your registration does
    password = "password123"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user_data = {
        "id": str(uuid.uuid4()),
        "username": f"testuser_{uuid.uuid4()}",  # Unique username with UUID
        "is_admin": False,
        "password": hashed_password.decode("utf-8"),  # Store hashed password
    }
    response = supabase.table("profiles").insert(user_data).execute()

    if response.data:
        # Return user data with plain password for testing
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "is_admin": user_data["is_admin"],
            "password": password,  # Return original password for login
        }
    else:
        pytest.fail(f"Failed to create test user: {response.error}")


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
