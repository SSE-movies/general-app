import json


def test_admin_page_access(admin_headers):
    response = admin_headers.get("/admin")
    assert response.status_code == 200
    assert b"User Management" in response.data


def test_admin_page_unauthorized(auth_headers):
    response = auth_headers.get("/admin")
    assert response.status_code == 302  # Redirects to login


def test_get_users_list(admin_headers):
    response = admin_headers.get("/api/users")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_reset_user_password(admin_headers, test_user):
    response = admin_headers.post(
        f"/api/users/{test_user['id']}/reset-password",
        json={"newPassword": "newpassword123"},
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Password updated successfully"


def test_delete_user(admin_headers, test_user):
    response = admin_headers.delete(f"/api/users/{test_user['id']}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "User deleted successfully"


def test_cannot_delete_admin(admin_headers, test_admin):
    response = admin_headers.delete(f"/api/users/{test_admin['id']}")
    assert response.status_code == 403  # Forbidden


def test_update_username(admin_headers, test_user):
    new_username = "updated_username"
    response = admin_headers.put(
        f"/api/users/{test_user['id']}/username",
        json={"newUsername": new_username},
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Username updated successfully"
