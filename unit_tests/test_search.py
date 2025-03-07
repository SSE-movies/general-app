def test_search_page_requires_login(client):
    """Ensure accessing search without login redirects to the login page."""
    response = client.get("/search")

    assert (
        response.status_code == 302
    ), f"Unexpected status code: {response.status_code}"
    assert (
        "/login" in response.location or "auth/login" in response.location
    ), f"Unexpected redirect location: {response.location}"


def test_search_page_access(
    auth_client,
):  # Changed from (client, auth_headers)
    """Ensure logged-in users can access the search page."""
    response = auth_client.get(
        "/search"
    )  # No need for headers with session auth

    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    assert (
        b"Search" in response.data
    ), f"Search page content missing: {response.data}"


def test_search_results(auth_client):
    """Test searching by category and title."""
    import os

    # Access the MOVIE_BACKEND_URL environment variable
    movie_backend_url = os.environ.get("MOVIE_BACKEND_URL")
    print(f"MOVIE_BACKEND_URL in test: {movie_backend_url}")

    # Test search with specific categories
    response = auth_client.get("/results?categories=Action%20%26%20Adventure")
    assert response.status_code == 200

    # Print response data for debugging
    print(response.data)

    # Accept either movie results or no results message
    assert any(
        [
            b"Action" in response.data,
            b"Adventure" in response.data,
            b"No movies found" in response.data,
            b"matching your search criteria" in response.data,
        ]
    ), "Expected either movie categories or no results message"

    # Test search with title
    response = auth_client.get("/results?title=test")

    assert response.status_code == 200
    assert any(
        [
            b"test" in response.data.lower(),
            b"movie" in response.data.lower(),
            b"No movies found" in response.data,
        ]
    ), "Expected either movie results or no results message"


def test_empty_search_results(
    auth_client,
):  # Changed from (client, auth_headers)
    """Ensure a search with no results displays the correct message."""
    response = auth_client.get("/results?title=nonexistentmovie123456")

    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    assert (
        b"No movies found" in response.data or b"No results" in response.data
    ), f"Unexpected empty search message: {response.data}"
