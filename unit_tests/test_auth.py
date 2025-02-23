import uuid
from src.database import supabase
import bcrypt


def test_login_page(client):
    """Ensure the login page loads correctly."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_successful_login(client, test_user):
    """Ensure a user can log in with correct credentials."""
    response = client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    # Should redirect to search page after login
    assert b"Search" in response.data


def test_invalid_login(client):
    """Ensure incorrect credentials result in an error message."""
    response = client.post(
        "/login", data={"username": "wronguser", "password": "wrongpass"}
    )

    assert response.status_code == 200
    assert b"Invalid credentials" in response.data


def test_register_page(client):
    """Ensure the registration page loads correctly."""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data


def test_successful_registration(client):
    """Ensure a new user can register successfully."""
    # Create test user data with valid password
    unique_username = f"testuser_{uuid.uuid4()}"
    valid_password = "TestPass123!"  # Meets password requirements

    response = client.post(
        "/register",
        data={"username": unique_username, "password": valid_password},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        b"Registration successful" in response.data
        or b"Login" in response.data
    )

    # Cleanup: Remove the test user
    try:
        supabase.table("profiles").delete().eq(
            "username", unique_username
        ).execute()
    except Exception as e:
        print(f"Failed to delete test user {unique_username}: {e}")


def test_duplicate_registration(client, test_user):
    """Test registration with existing username."""
    response = client.post(
        "/register",
        data={"username": test_user["username"], "password": "TestPass123!"},
    )

    assert response.status_code == 200
    assert b"Username already exists" in response.data


def test_invalid_password_registration(client):
    """Test registration with invalid password."""
    response = client.post(
        "/register",
        data={
            "username": f"testuser_{uuid.uuid4()}",
            "password": "weak",  # Too short, missing requirements
        },
    )

    assert response.status_code == 200
    assert b"Password must be" in response.data


def test_logout(auth_client):
    """Test logout functionality."""
    # First verify we're logged in
    response = auth_client.get("/search")
    assert response.status_code == 200

    # Then test logout
    response = auth_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

    # Verify we can't access protected page after logout
    response = auth_client.get("/search")
    assert response.status_code in [302, 303]  # Should redirect to login
