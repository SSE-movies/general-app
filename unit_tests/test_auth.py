import json
import uuid  # Import uuid for generating unique usernames
from src.database import supabase


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
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    assert b"Search" in response.data, f"Login did not redirect properly: {response.data}"


def test_invalid_login(client):
    """Ensure incorrect credentials result in an error message."""
    response = client.post(
        "/login", data={"username": "wronguser", "password": "wrongpass"}
    )
    assert response.status_code in [200, 401], f"Unexpected status code: {response.status_code}"
    assert (
        b"Invalid credentials" in response.data or b"Incorrect username or password" in response.data
    ), f"Unexpected error message: {response.data}"


def test_register_page(client):
    """Ensure the registration page loads correctly."""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data


def test_successful_registration(client):
    """Ensure a new user can register successfully."""
    unique_username = f"user_{uuid.uuid4().hex[:8]}"  # Generate a unique username

    response = client.post(
        "/register",
        data={"username": unique_username, "password": "newpass"},
        follow_redirects=True,
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    assert (
        b"Registration successful" in response.data
        or b"Account created successfully" in response.data
    ), f"Unexpected message: {response.data}"

    # Cleanup: Remove the test user from the database
    supabase.table("profiles").delete().eq("username", unique_username).execute()


def test_logout(auth_headers):
    """Ensure a user can log out successfully."""
    response = auth_headers.get("/logout", follow_redirects=True)
    assert response.status_code in [200, 302], f"Unexpected status code: {response.status_code}"
    assert (
        b"Login" in response.data or b"Successfully logged out" in response.data
    ), f"Unexpected logout message: {response.data}"
