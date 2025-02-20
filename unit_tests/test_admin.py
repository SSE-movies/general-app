import json


def test_admin_page_access(admin_headers):
    """Ensure an admin can access the admin page."""
    response = admin_headers.get("/admin")
    assert response.status_code == 200
    assert b"User Management" in response.data


def test_admin_page_unauthorized(auth_headers):
    """Ensure non-admin users cannot access the admin page."""
    response = auth_headers.get("/admin")
    assert response.status_code in [302, 403]  # Some apps return 403 instead of redirect
    if response.status_code == 302:
        assert "/login" in response.location  # Redirects to login page


def test_get_users_list(admin_headers):
    """Ensure the admin can retrieve a list of users."""
    response = admin_headers.get("/api/users")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list), "Expected a list of users, but got something else."


def test_reset_user_password(admin_headers, test_user):
    """Ensure an admin can reset a user's password."""
    response = admin_headers.post(
        f"/api/users/{test_user['id']}/reset-password",
        json={"newPassword": "newpassword123"},
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = json.loads(response.data)
    assert data.get("message") == "Password updated successfully", f"Unexpected message: {data}"


def test_delete_user(admin_headers, test_user):
    """Ensure an admin can delete a user."""
    response = admin_headers.delete(f"/api/users/{test_user['id']}")
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = json.loads(response.data)
    assert data.get("message") == "User deleted successfully", f"Unexpected message: {data}"


def test_cannot_delete_admin(admin_headers, test_admin):
    """Ensure an admin cannot delete another admin."""
    response = admin_headers.delete(f"/api/users/{test_admin['id']}")
    assert response.status_code == 403, f"Expected 403 Forbidden, but got {response.status_code}"


def test_update_username(admin_headers, test_user):
    """Ensure an admin can update a user's username."""
    new_username = "updated_username"

    # Delete the username first to avoid duplicate key constraint errors
    supabase.table("profiles").delete().eq("username", new_username).execute()

    response = admin_headers.put(
        f"/api/users/{test_user['id']}/username",
        json={"newUsername": new_username},
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = json.loads(response.data)
    assert data.get("message") == "Username updated successfully", f"Unexpected message: {data}"
