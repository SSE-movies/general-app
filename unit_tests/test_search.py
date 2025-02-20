def test_search_page_requires_login(client):
    response = client.get("/search")
    assert response.status_code == 302  # Redirects to login
    assert "/login" in response.location


def test_search_page_access(auth_headers):
    response = auth_headers.get("/search")
    assert response.status_code == 200
    assert b"Search" in response.data


def test_search_results(auth_headers):
    # Test search with specific categories
    response = auth_headers.get("/results?categories=Action+%26+Adventure")
    assert response.status_code == 200

    # Test search with title
    response = auth_headers.get("/results?title=test")
    assert response.status_code == 200


def test_empty_search_results(auth_headers):
    response = auth_headers.get("/results?title=nonexistentmovie123456")
    assert response.status_code == 200
    assert b"No movies found" in response.data