import pytest
from src import create_app
from src.database import supabase
import bcrypt


@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True, "WTF_CSRF_ENABLED": False})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_user():
    """Creates a unique test user and ensures no duplicate entry exists."""
    username = "testuser"
    password = "testpass"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    # Ensure the user does not exist before inserting
    supabase.table("profiles").delete().eq("username", username).execute()

    user_data = {
        "username": username,
        "password": hashed_password.decode("utf-8"),
        "is_admin": False,
    }

    # Insert user and handle any failure
    response = supabase.table("profiles").insert(user_data).execute()
    if not response.data:
        raise Exception(f"Failed to insert test user: {response}")

    user = response.data[0]
    yield {"username": username, "password": password, "id": user["id"]}

    # Cleanup: Ensure the user is deleted after tests
    supabase.table("profiles").delete().eq("username", username).execute()


@pytest.fixture
def test_admin():
    """Creates a unique test admin user and ensures no duplicate entry exists."""
    username = "testadmin"
    password = "adminpass"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    # Ensure the admin does not exist before inserting
    supabase.table("profiles").delete().eq("username", username).execute()

    admin_data = {
        "username": username,
        "password": hashed_password.decode("utf-8"),
        "is_admin": True,
    }

    # Insert admin user and handle any failure
    response = supabase.table("profiles").insert(admin_data).execute()
    if not response.data:
        raise Exception(f"Failed to insert test admin: {response}")

    admin = response.data[0]
    yield {"username": username, "password": password, "id": admin["id"]}

    # Cleanup: Ensure the admin is deleted after tests
    supabase.table("profiles").delete().eq("username", username).execute()


@pytest.fixture
def auth_headers(client, test_user):
    """Logs in as a test user and returns authenticated client."""
    response = client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200, "Test user login failed"
    return client


@pytest.fixture
def admin_headers(client, test_admin):
    """Logs in as an admin user and returns authenticated client."""
    response = client.post(
        "/login",
        data={
            "username": test_admin["username"],
            "password": test_admin["password"],
        },
    )
    assert response.status_code == 200, "Test admin login failed"
    return client
