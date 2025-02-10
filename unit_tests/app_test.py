from ..app import app

# import requests


# test correct loading of homepage
def test_homepage_loads_correctly():
    # Create a test client to allow simulation of HTTP requests to the app
    with app.test_client() as client:
        response = client.get("/")

    # Assert the request succeeded (HTTP 200)
    assert response.status_code == 200
