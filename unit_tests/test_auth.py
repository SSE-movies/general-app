import json
import uuid  # Import uuid for generating unique usernames
from src.database import supabase


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_successful_login(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Search" in response.data


def test_invalid_login(client):
    response = client.post(
        "/login", data={"username": "wronguser", "password": "wrongpass"}
    )
    assert b"Invalid credentials" in response.data


def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data


def test_successful_registration(client):
    unique_username = (
        f"user_{uuid.uuid4().hex[:8]}"  # Generate a unique username
    )

    response = client.post(
        "/register",
        data={"username": unique_username, "password": "newpass"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    supabase.table("profiles").delete().eq(
        "username", unique_username
    ).execute()


def test_logout(auth_headers):
    response = auth_headers.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data
