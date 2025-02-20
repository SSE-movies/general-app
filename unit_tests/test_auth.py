import json
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
    response = client.post(
        "/register",
        data={"username": "newuser", "password": "newpass"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    # Cleanup
    supabase.table("profiles").delete().eq("username", "newuser").execute()


def test_logout(auth_headers):
    response = auth_headers.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data
