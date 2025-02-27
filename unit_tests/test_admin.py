import pytest
import uuid
from src import create_app
from src.database import supabase


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
    """Create a regular test user in Supabase."""
    user_data = {
        "id": str(uuid.uuid4()),  # Ensure UUID format
        "username": "testuser",
        "password": "password123",
        "is_admin": False,
    }
    response = supabase.table("profiles").insert(user_data).execute()

    if response.data:
        return user_data  # Return the created user data
    else:
        pytest.fail(f"Failed to create test user: {response.error}")


@pytest.fixture(scope="module")
def test_admin():
    """Create an admin user in Supabase."""
    admin_data = {
        "id": str(uuid.uuid4()),
        "username": "adminuser",
        "password": "adminpass123",
        "is_admin": True,
    }
    response = supabase.table("profiles").insert(admin_data).execute()

    if response.data:
        return admin_data  # Return the created admin user data
    else:
        pytest.fail(f"Failed to create test admin: {response.error}")


@pytest.fixture(scope="module")
def admin_user():
    """Get the existing admin user for tests."""
    admin = (
        supabase.table("profiles")
        .select("*")
        .eq("is_admin", True)
        .limit(1)
        .execute()
    )
    if not admin.data:
        pytest.skip("No admin user found in database")
    return admin.data[0]
