"""Database and API configuration module"""

import logging
import os
import requests
from flask import request
from supabase import create_client, Client

# Set up logging
logger = logging.getLogger(__name__)

# Constants
TIMEOUT_SECONDS = 10  # Add a reasonable timeout constant

# Get configuration from environment
MOVIES_API_URL = os.environ.get("MOVIES_API_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
WATCHLIST_BACKEND_URL = os.environ.get("WATCHLIST_BACKEND_URL")

logger.debug(f"MOVIES_API_URL: {MOVIES_API_URL}")
logger.debug(f"WATCHLIST_BACKEND_URL: {WATCHLIST_BACKEND_URL}")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_movies():
    """Get all movies for initial loading."""
    try:
        response = requests.get(MOVIES_API_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json().get("movies", [])
    except requests.RequestException as e:
        logger.error(f"Error fetching movies: {e}")
        return []


def _build_movie_params(query_params, page):
    """Build query parameters for the movies API request."""
    params = {
        "page": page,
        "per_page": 10  # Fixed value for results per page
    }
    if query_params:
        param_mapping = {
            "title": "title",
            "type": "type",
            "categories": "categories",
            "release_year": "release_year"
        }
        params.update({
            api_param: query_params[param_name]
            for param_name, api_param in param_mapping.items()
            if query_params.get(param_name)
        })
    return params

def _normalize_movie_fields(movie):
    """Normalize field names in movie data."""
    field_mapping = {
        "listed_in": "listedIn",
        "show_id": "showId",
        "release_year": "releaseYear"
    }
    for old_field, new_field in field_mapping.items():
        if old_field in movie:
            movie[new_field] = movie.pop(old_field)
    return movie

def get_filtered_movies(query_params=None, username=None):
    """
    Fetches and filters movies based on search criteria.
    Marks watchlist status if username is provided.
    Passes pagination parameters to the API so that only 10 movies are fetched at a time.
    """
    try:
        # Get pagination parameters and build query
        page = request.args.get("page", 1, type=int)
        params = _build_movie_params(query_params, page)

        # Fetch filtered movies
        response = requests.get(
            MOVIES_API_URL, params=params, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        movies = data.get("movies", [])

        # Get watchlist status for all movies if username provided
        watchlist_status = {}
        if username and movies:
            # Extract show IDs, handling both field names
            show_ids = [
                movie.get("show_id") or movie.get("showId")
                for movie in movies
            ]
            try:
                watchlist_response = requests.post(
                    f"{WATCHLIST_BACKEND_URL}/watchlist/batch",
                    json={
                        "username": username,
                        "showIds": show_ids
                    },
                    timeout=TIMEOUT_SECONDS
                )
                watchlist_response.raise_for_status()
                watchlist_status = watchlist_response.json()
            except Exception as e:
                logger.error(
                    f"Error checking watchlist status: {e}"
                )

        # Process each movie
        for movie in movies:
            movie = _normalize_movie_fields(movie)
            show_id = movie.get("showId")
            movie["in_watchlist"] = watchlist_status.get(
                show_id, {}).get("in_watchlist", False) if username else False

        # Determine pagination flags
        results_per_page = 10
        has_next = len(movies) == results_per_page
        has_prev = page > 1

        return movies, page, has_next, has_prev, None

    except requests.RequestException as e:
        logger.error(f"Error fetching filtered movies: {e}")
        return [], 1, False, False, None


def get_unique_categories():
    """Get list of unique categories from all movies."""
    try:
        response = requests.get(MOVIES_API_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        movies = response.json().get("movies", [])

        # Extract and flatten categories
        categories = set()
        for movie in movies:
            # Check both possible field names (listed_in and listedIn)
            category_field = (
                movie.get("listed_in") or movie.get("listedIn") or ""
            )
            if category_field:
                movie_categories = category_field.split(",")
                categories.update(
                    cat.strip() for cat in movie_categories if cat.strip()
                )

        return sorted(list(categories))
    except requests.RequestException as e:
        logger.error(f"Error fetching categories: {e}")
        return []


def get_movie_by_id(movie_id):
    """Get a specific movie by its ID."""
    try:
        response = requests.get(
            f"{MOVIES_API_URL}/{movie_id}", timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching movie {movie_id}: {e}")
        return None


def check_movie_exists_by_title(title, username=None):
    """
    Check if a movie exists in the database by title.
    Returns the movie if found, None otherwise.
    """
    try:
        # Build query params
        params = {"title": title, "per_page": 1}  # We only need one match

        # Fetch filtered movies
        response = requests.get(
            MOVIES_API_URL, params=params, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        movies = data.get("movies", [])

        if not movies:
            return None

        movie = movies[0]

        # Normalise field names
        if "listed_in" in movie:
            movie["listedIn"] = movie.pop("listed_in")
        if "show_id" in movie:
            movie["showId"] = movie.pop("show_id")
        if "release_year" in movie:
            movie["releaseYear"] = movie.pop("release_year")

        # Check watchlist status if username is provided
        if username:
            try:
                watchlist_response = requests.get(
                    f"{WATCHLIST_BACKEND_URL}/watchlist/status/{username}/{movie['showId']}",
                    timeout=TIMEOUT_SECONDS
                )
                watchlist_response.raise_for_status()
                watchlist_status = watchlist_response.json()
                movie["in_watchlist"] = watchlist_status.get("in_watchlist", False)
            except Exception as e:
                logger.error(f"Error checking watchlist status: {e}")
                movie["in_watchlist"] = False

        return movie

    except requests.RequestException as e:
        logger.error(f"Error checking movie existence: {e}")
        return None
