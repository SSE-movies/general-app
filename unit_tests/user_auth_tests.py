import pytest
from app import app, supabase
import bcrypt


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers():
    return {"Content-Type": "application/x-www-form-urlencoded"}


@pytest.fixture
def test_user():
    # Create a test user
    username = "testuser"
    password = "testpass123"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    # Insert test user into database
    user_data = {
        "username": username,
        "password": hashed_password.decode("utf-8"),
        "is_admin": False,
    }

    # Create the user
    response = supabase.table("profiles").insert(user_data).execute()
    user = response.data[0]

    yield {
        "id": user["id"],
        "username": username,
        "password": "testpass123",  # Plain password for testing
        "is_admin": False,
    }

    # Cleanup: Delete test user after tests
    supabase.table("profiles").delete().eq("username", username).execute()


@pytest.fixture
def test_admin():
    # Create a test admin user
    username = "testadmin"
    password = "adminpass123"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    # Insert test admin into database
    admin_data = {
        "username": username,
        "password": hashed_password.decode("utf-8"),
        "is_admin": True,
    }

    # Create the admin
    response = supabase.table("profiles").insert(admin_data).execute()
    admin = response.data[0]

    yield {
        "id": admin["id"],
        "username": username,
        "password": "adminpass123",  # Plain password for testing
        "is_admin": True,
    }

    # Cleanup: Delete test admin after tests
    supabase.table("profiles").delete().eq("username", username).execute()


def test_login_page_loads(client):
    """Test that login page loads correctly"""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_successful_login(client, auth_headers, test_user):
    """Test successful login with valid credentials"""
    response = client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 302  # Redirect after successful login
    assert "/search" in response.location  # Should redirect to search page


def test_failed_login_wrong_password(client, auth_headers, test_user):
    """Test login failure with wrong password"""
    response = client.post(
        "/login",
        data={"username": test_user["username"], "password": "wrongpassword"},
        headers=auth_headers,
    )
    assert response.status_code == 200  # Stay on login page
    assert b"Invalid credentials" in response.data


def test_failed_login_nonexistent_user(client, auth_headers):
    """Test login failure with non-existent user"""
    response = client.post(
        "/login",
        data={"username": "nonexistentuser", "password": "anypassword"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data


def test_register_new_user(client, auth_headers):
    """Test successful user registration"""
    response = client.post(
        "/register",
        data={"username": "newuser", "password": "newpass123"},
        headers=auth_headers,
    )
    assert (
        response.status_code == 302
    )  # Redirect after successful registration
    assert "/login" in response.location

    # Cleanup: Delete the created user
    supabase.table("profiles").delete().eq("username", "newuser").execute()


def test_register_existing_username(client, auth_headers, test_user):
    """Test registration failure with existing username"""
    response = client.post(
        "/register",
        data={"username": test_user["username"], "password": "somepassword"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert b"Username already exists" in response.data


def test_admin_access(client, auth_headers, test_admin):
    """Test admin page access with admin user"""
    # Login as admin first
    client.post(
        "/login",
        data={
            "username": test_admin["username"],
            "password": test_admin["password"],
        },
        headers=auth_headers,
    )

    # Try accessing admin page
    response = client.get("/admin")
    assert response.status_code == 200
    assert b"User Management" in response.data


def test_non_admin_access_restricted(client, auth_headers, test_user):
    """Test admin page access restriction for non-admin users"""
    # Login as regular user first
    client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
        headers=auth_headers,
    )

    # Try accessing admin page
    response = client.get("/admin")
    assert response.status_code == 302  # Should redirect
    assert "/login" in response.location


def test_logout(client, auth_headers, test_user):
    """Test logout functionality"""
    # Login first
    client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
        headers=auth_headers,
    )

    # Then logout
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/" in response.location  # Should redirect to index

    # Try accessing protected route after logout
    response = client.get("/search")
    assert response.status_code == 302
    assert "/login" in response.location


def test_protected_route_access(client, auth_headers, test_user):
    """Test access to protected routes with and without authentication"""
    # Try accessing protected route without login
    response = client.get("/search")
    assert response.status_code == 302
    assert "/login" in response.location

    # Login
    client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
        headers=auth_headers,
    )

    # Try accessing protected route after login
    response = client.get("/search")
    assert response.status_code == 200
