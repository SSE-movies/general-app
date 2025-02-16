import pytest
from ..app import app

# import requests


# ---------------------------------------------------------------------------
# Pytest Fixture: 'client'
# ---------------------------------------------------------------------------
# This fixture sets up a test client for the Flask app, which simulates HTTP
# requests in a testing environment. This client will be passed to each test
# function that requires it.
@pytest.fixture
def client():
    # Enable testing mode to propagate exceptions to the test client
    app.config["TESTING"] = True

    # Create a test client that can be used to make HTTP requests to the app.
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Helper Function: login_test_user
# ---------------------------------------------------------------------------
# This function simulates a logged-in user by directly setting the session
# variables. It is used in tests to bypass the login process.
def login_test_user(client):
    with client.session_transaction() as sess:
        # Set dummy variables
        sess["user_id"] = "test_user_id"
        sess["username"] = "test_user"
        # Set admin flag to False for non-admin tests
        sess["is_admin"] = False


# ---------------------------------------------------------------------------
# Test: Homepage Loads Correctly
# ---------------------------------------------------------------------------
def test_homepage_loads_correctly(client):
    # Send a GET request to the homepage
    response = client.get("/")

    # Assert that the homepage returns HTTP 200 (OK)
    assert response.status_code == 200
