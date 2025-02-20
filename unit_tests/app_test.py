import pytest

# from ..app import app
import unittest
from unittest.mock import patch, Mock
from app import app, MOVIES_API_URL

# import requests


# # ---------------------------------------------------------------------------
# # Pytest Fixture: 'client'
# # ---------------------------------------------------------------------------
# # This fixture sets up a test client for the Flask app, which simulates HTTP
# # requests in a testing environment. This client will be passed to each test
# # function that requires it.
# @pytest.fixture
# def client():
#     # Enable testing mode to propagate exceptions to the test client
#     app.config["TESTING"] = True

#     # Create a test client that can be used to make HTTP requests to the app.
#     with app.test_client() as client:
#         yield client


# # ---------------------------------------------------------------------------
# # Helper Function: login_test_user
# # ---------------------------------------------------------------------------
# # This function simulates a logged-in user by directly setting the session
# # variables. It is used in tests to bypass the login process.
# def login_test_user(client):
#     with client.session_transaction() as sess:
#         # Set dummy variables
#         sess["user_id"] = "test_user_id"
#         sess["username"] = "test_user"
#         # Set admin flag to False for non-admin tests
#         sess["is_admin"] = False


# # ---------------------------------------------------------------------------
# # Test: Homepage Loads Correctly
# # ---------------------------------------------------------------------------
# def test_homepage_loads_correctly(client):
#     # Send a GET request to the homepage
#     response = client.get("/")

#     # Assert that the homepage returns HTTP 200 (OK)
#     assert response.status_code == 200


class AppTestCase(unittest.TestCase):
    def setUp(self):
        # Enable testing mode and get the test client.
        app.testing = True
        self.client = app.test_client()

    def login(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = "test_user_id"
            sess["username"] = "testuser"
            sess["is_admin"] = False

    @patch("app.get_unique_categories")
    @patch("app.requests.get")
    def test_search_get_no_filter(
        self, mock_requests_get, mock_get_unique_categories
    ):
        """Test GET /search when no categories are provided (should return no movies)."""
        self.login()

        # Set up a fake movies API response.
        fake_movies_data = {
            "movies": [
                {
                    "listedIn": "Documentaries, International Movies",
                    "title": "Movie1",
                },
                {"listedIn": "Action, Adventure", "title": "Movie2"},
            ]
        }
        fake_response = Mock()
        fake_response.json.return_value = fake_movies_data
        fake_response.raise_for_status = lambda: None
        mock_requests_get.return_value = fake_response

        # Fake unique categories.
        mock_get_unique_categories.return_value = [
            "Documentaries",
            "International Movies",
            "Action",
            "Adventure",
        ]

        # Send a GET request without any 'categories' in the query string.
        response = self.client.get("/search")
        self.assertEqual(response.status_code, 200)

        # Since no categories were selected, the filtering loop should yield an empty list.
        # Check that neither movie title appears in the rendered HTML.
        self.assertNotIn(b"Movie1", response.data)
        self.assertNotIn(b"Movie2", response.data)
        # Verify that the username is present.
        self.assertIn(b"testuser", response.data)

    @patch("app.get_unique_categories")
    @patch("app.requests.get")
    def test_search_post_with_filter(
        self, mock_requests_get, mock_get_unique_categories
    ):
        """Test POST /search with selected categories filters the movies correctly."""
        self.login()

        fake_movies_data = {
            "movies": [
                {
                    "listedIn": "Documentaries, International Movies",
                    "title": "Movie1",
                },
                {"listedIn": "Action, Adventure", "title": "Movie2"},
            ]
        }
        fake_response = Mock()
        fake_response.json.return_value = fake_movies_data
        fake_response.raise_for_status = lambda: None
        mock_requests_get.return_value = fake_response

        mock_get_unique_categories.return_value = [
            "Documentaries",
            "International Movies",
            "Action",
            "Adventure",
        ]

        # Send a POST request with a category filter that should match Movie1.
        data = {"categories": ["Documentaries"]}
        response = self.client.post("/search", data=data)
        self.assertEqual(response.status_code, 200)

        # Check that the filtered movies include Movie1 and not Movie2.
        self.assertIn(b"Movie1", response.data)
        self.assertNotIn(b"Movie2", response.data)
        self.assertIn(b"testuser", response.data)

    @patch("app.get_unique_categories")
    @patch("app.requests.get")
    def test_results(self, mock_requests_get, mock_get_unique_categories):
        """Test GET /results with query parameters building proper API call."""
        self.login()

        # Fake response for the external API call.
        fake_movies_data = {
            "movies": [
                {
                    "listedIn": "Documentaries, International Movies",
                    "title": "Movie1",
                }
            ]
        }
        fake_response = Mock()
        fake_response.json.return_value = fake_movies_data
        fake_response.raise_for_status = lambda: None
        mock_requests_get.return_value = fake_response

        mock_get_unique_categories.return_value = [
            "Documentaries",
            "International Movies",
            "Action",
            "Adventure",
        ]

        # Build query string with multiple categories.
        query_string = "title=Movie&type=Action&categories=Documentaries&categories=Action&release_year=2020"
        response = self.client.get(f"/results?{query_string}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Movie1", response.data)
        self.assertIn(b"testuser", response.data)

        # Ensure that the API call was made with the proper query parameters.
        # Note: for categories, our route joins the list into a comma-separated string.
        expected_params = {
            "title": "Movie",
            "type": "Action",
            "categories": "Documentaries,Action",
            "release_year": "2020",
        }
        mock_requests_get.assert_called_with(
            MOVIES_API_URL, params=expected_params
        )


if __name__ == "__main__":
    unittest.main()
