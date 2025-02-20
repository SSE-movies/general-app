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

    # Insert test user into database
    response = supabase.table("profiles").insert(user_data).execute()
    user = response.data[0]

    yield {"username": username, "password": password, "id": user["id"]}

    # Cleanup: Delete test user
    supabase.table("profiles").delete().eq("username", username).execute()


@pytest.fixture
def test_admin():
    # Create a test admin user
    username = "testadmin"
    password = "adminpass"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    admin_data = {
        "username": username,
        "password": hashed_password.decode("utf-8"),
        "is_admin": True,
    }

    # Insert test admin into database
    response = supabase.table("profiles").insert(admin_data).execute()
    admin = response.data[0]

    yield {"username": username, "password": password, "id": admin["id"]}

    # Cleanup: Delete test admin
    supabase.table("profiles").delete().eq("username", username).execute()


@pytest.fixture
def auth_headers(client, test_user):
    # Login and get session
    client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    return client


@pytest.fixture
def admin_headers(client, test_admin):
    # Login as admin and get session
    client.post(
        "/login",
        data={
            "username": test_admin["username"],
            "password": test_admin["password"],
        },
    )
    return client
