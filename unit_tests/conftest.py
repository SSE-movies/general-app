import pytest
import uuid
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
    user_data = {
        "id": str(uuid.uuid4()),
        "username": f"testuser_{uuid.uuid4()}",  # Unique username with UUID
        "is_admin": False,
        "password": "password123",
    }
    response = supabase.table("profiles").insert(user_data).execute()

    if response.data:
        return user_data  # Return the created user data
    else:
        pytest.fail(f"Failed to create test user: {response.error}")


@pytest.fixture(scope="module")
def test_admin():
    """Create an admin user in Supabase with a UUID."""
    admin_data = {
        "id": str(uuid.uuid4()),
        "username": f"adminuser_{uuid.uuid4()}",  # Unique username for admin
        "is_admin": True,
        "password": "adminpass123",
    }
    response = supabase.table("profiles").insert(admin_data).execute()

    if response.data:
        return admin_data  # Return the created admin user data
    else:
        pytest.fail(f"Failed to create test admin: {response.error}")


@pytest.fixture(scope="module")
def auth_headers(client, test_user):
    """Return authentication headers for a regular user."""
    response = client.post(
        "/auth/login",
        json={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    token = response.json.get("access_token")

    if not token:
        pytest.fail("Failed to obtain auth token for test user")

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def admin_headers(client, test_admin):
    """Return authentication headers for an admin user."""
    response = client.post(
        "/auth/login",
        json={
            "username": test_admin["username"],
            "password": test_admin["password"],
        },
    )
    token = response.json.get("access_token")

    if not token:
        pytest.fail("Failed to obtain auth token for admin user")

    return {"Authorization": f"Bearer {token}"}
