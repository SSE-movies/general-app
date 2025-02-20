import json
from src.database import supabase


def test_admin_page_access(client, admin_headers):
    """Ensure an admin can access the admin page."""
    response = client.get("/admin")
    assert response.status_code == 200
    assert b"User Management" in response.data


def test_admin_page_unauthorized(client, auth_headers):
    """Ensure non-admin users cannot access the admin page."""
    response = client.get("/admin")
    assert response.status_code in [
        302,
        403,
    ]  # Some apps return 403 instead of redirect
    if response.status_code == 302:
        assert "/login" in response.location  # Redirects to login page


def test_get_users_list(client, admin_headers):
    """Ensure the admin can retrieve a list of users."""
    response = client.get("/api/users")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(
        data, list
    ), "Expected a list of users, but got something else."


def test_reset_user_password(client, admin_headers, test_user):
    """Ensure an admin can reset a user's password."""
    response = client.post(
        f"/api/users/{test_user['id']}/reset-password",
        json={"newPassword": "newpassword123"},
        content_type="application/json",
    )
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    data = json.loads(response.data)
    assert (
        data.get("message") == "Password updated successfully"
    ), f"Unexpected message: {data}"


def test_delete_user(client, admin_headers, test_user):
    """Ensure an admin can delete a user."""
    response = client.delete(f"/api/users/{test_user['id']}")
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    data = json.loads(response.data)
    assert (
        data.get("message") == "User deleted successfully"
    ), f"Unexpected message: {data}"


def test_cannot_delete_admin(client, admin_headers, test_admin):
    """Ensure an admin cannot delete another admin."""
    response = client.delete(f"/api/users/{test_admin['id']}")
    assert (
        response.status_code == 403
    ), f"Expected 403 Forbidden, but got {response.status_code}"


def test_update_username(client, admin_headers, test_user):
    """Ensure an admin can update a user's username."""
    new_username = "updated_username"

    # Delete the username first to avoid duplicate key constraint errors
    supabase.table("profiles").delete().eq("username", new_username).execute()

    response = client.put(
        f"/api/users/{test_user['id']}/username",
        json={"newUsername": new_username},
        content_type="application/json",
    )
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    data = json.loads(response.data)
    assert (
        data.get("message") == "Username updated successfully"
    ), f"Unexpected message: {data}"
