"""Database (and API) configuration module"""

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
MOVIE_BACKEND_URL = os.environ.get("MOVIE_BACKEND_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
WATCHLIST_BACKEND_URL = os.environ.get("WATCHLIST_BACKEND_URL")

logger.debug(f"MOVIE_BACKEND_URL: {MOVIE_BACKEND_URL}")
logger.debug(f"WATCHLIST_BACKEND_URL: {WATCHLIST_BACKEND_URL}")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_movies():
    """Get all movies for initial loading."""
    try:
        response = requests.get(MOVIE_BACKEND_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json().get("movies", [])
    except requests.RequestException as e:
        logger.error(f"Error fetching movies: {e}")
        return []


def _build_movie_params(query_params, page):
    """Build query parameters for the movies API request."""
    params = {"page": page, "per_page": 10}  # Fixed value for results per page
    if query_params:
        # Log the raw query parameters for debugging
        logger.info(f"Raw query parameters: {query_params}")
        param_mapping = {
            "title": "title",
            "type": "type",
            "categories": "categories",
            "release_year": "release_year",
        }
        # Handle each parameter individually for better control
        for param_name, api_param in param_mapping.items():
            if query_params.get(param_name):
                # Special handling for type parameter
                if param_name == "type":
                    # Log the type value for debugging
                    logger.info(f"Type parameter value: '{query_params[param_name]}'")
                    # Handle different variations of TV Show type
                    type_value = query_params[param_name].lower()
                    if type_value in ("tv", "tv show", "tvshow"):
                        params[api_param] = "TV Show"
                    elif type_value == "movie":
                        params[api_param] = "Movie"
                    else:
                        # Pass through any other values
                        params[api_param] = query_params[param_name]
                # Special handling for categories with special characters
                elif param_name == "categories":
                    # Handle both single category and list of categories
                    categories = query_params[param_name]
                    if isinstance(categories, list):
                        # If it's already a list, use it as is
                        params[api_param] = categories
                    else:
                        # If it's a single string, use it directly
                        # The API will handle URL decoding
                        params[api_param] = categories
                    logger.info(f"Categories parameter: {params[api_param]}")
                else:
                    # Handle other parameters normally
                    params[api_param] = query_params[param_name]
    # Log the final parameters being sent to the API
    logger.info(f"Final API parameters: {params}")
    return params


def _normalize_movie_fields(movie):
    """Normalize field names in movie data."""
    field_mapping = {
        "listed_in": "listedIn",
        "show_id": "showId",
        "release_year": "releaseYear",
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
        # Log the incoming query parameters for debugging
        logger.info(f"Incoming query parameters: {query_params}")
        # Make a copy of query_params to avoid modifying the original
        if query_params:
            modified_params = query_params.copy()
            # Check if we're filtering for TV Shows (handle different variations)
            tv_type_values = ["tv", "tv show", "tvshow"]
            if (modified_params.get("type") and
                    modified_params.get("type").lower() in tv_type_values):
                logger.info(f"TV Show filter detected (value: {modified_params.get('type')})")
                # Set the type to "TV Show" for consistency
                modified_params["type"] = "TV Show"
                # First attempt with the standard format
                params = _build_movie_params(modified_params, page)
                response = requests.get(
                    MOVIE_BACKEND_URL, params=params, timeout=TIMEOUT_SECONDS
                )
                response.raise_for_status()
                data = response.json()
                movies = data.get("movies", [])
                logger.info(f"TV Show query returned {len(movies)} results")
                # If no results, try alternative formats
                if len(movies) == 0:
                    movies = _try_alternative_tv_formats(params)
                # Process the movies we found (if any)
                if movies:
                    # Get watchlist status and process movies
                    return _process_movies_with_watchlist(movies, username, page)
        # If we're not filtering for TV Shows or if we didn't return early above
        params = _build_movie_params(query_params, page)
        # Fetch filtered movies
        logger.info(f"Sending request to {MOVIE_BACKEND_URL} with params: {params}")
        try:
            response = requests.get(
                MOVIE_BACKEND_URL, params=params, timeout=TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
            movies = data.get("movies", [])
            # Log the number of movies returned
            logger.info(f"Received {len(movies)} movies from API")
            # Process movies with watchlist status
            return _process_movies_with_watchlist(movies, username, page)
        except requests.HTTPError as e:
            logger.error(f"HTTP error fetching movies: {e}")
            # Return empty results with error message
            error_message = f"Error fetching movies: {e}"
            return [], 1, False, False, error_message
    except requests.RequestException as e:
        logger.error(f"Error fetching filtered movies: {e}")
        # Return empty results with error message
        error_message = f"Error fetching movies: {e}"
        return [], 1, False, False, error_message


def _try_alternative_tv_formats(params):
    """Try alternative formats for TV Show type."""
    # Try common alternative formats for "TV Show"
    alternatives = ["TV", "tv show", "tv_show", "tvshow", "series"]
    for alt in alternatives:
        logger.info(f"Trying alternative TV Show format: '{alt}'")
        alt_params = params.copy()
        alt_params["type"] = alt
        try:
            alt_response = requests.get(
                MOVIE_BACKEND_URL, params=alt_params, timeout=TIMEOUT_SECONDS
            )
            alt_response.raise_for_status()
            alt_data = alt_response.json()
            alt_movies = alt_data.get("movies", [])
            logger.info(
                f"Alternative format '{alt}' returned {len(alt_movies)} results"
            )
            if len(alt_movies) > 0:
                return alt_movies
        except requests.RequestException as e:
            logger.error(f"Error with alternative format '{alt}': {e}")
    # If no results found with any format
    return []


def _process_movies_with_watchlist(movies, username, page):
    """Process movies and add watchlist status."""
    # Get watchlist status for all movies if username provided
    watchlist_status = {}
    if username and movies:
        # Extract show IDs, handling both field names
        show_ids = [
            movie.get("show_id") or movie.get("showId") for movie in movies
        ]
        try:
            watchlist_response = requests.post(
                f"{WATCHLIST_BACKEND_URL}/watchlist/batch",
                json={"username": username, "showIds": show_ids},
                timeout=TIMEOUT_SECONDS,
            )
            watchlist_response.raise_for_status()
            watchlist_status = watchlist_response.json()
        except Exception as e:
            logger.error(f"Error checking watchlist status: {e}")
    # Process each movie
    for movie in movies:
        movie = _normalize_movie_fields(movie)
        show_id = movie.get("showId")
        movie["in_watchlist"] = (
            watchlist_status.get(show_id, {}).get("in_watchlist", False)
            if username
            else False
        )
    # Determine pagination flags
    results_per_page = 10
    has_next = len(movies) == results_per_page
    has_prev = page > 1
    return movies, page, has_next, has_prev, None


def get_unique_categories():
    """Get unique categories from movies table."""
    try:
        response = supabase.table("movies").select("listedIn").execute()
        # Create a set to store unique categories
        unique_categories = set()
        # Parse through each movie's categories
        for movie in response.data:
            if movie.get("listedIn"):
                # Split categories if it's a string containing multiple categories
                if isinstance(movie["listedIn"], str):
                    categories = movie["listedIn"].split(",")
                    # Strip whitespace and add each category
                    for category in categories:
                        unique_categories.add(category.strip())
                # If it's already a list, add each category
                elif isinstance(movie["listedIn"], list):
                    for category in movie["listedIn"]:
                        unique_categories.add(category.strip())
        # Convert set to sorted list and return
        return sorted(list(unique_categories))
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []


def get_movie_details_by_id(movie_id):
    """Get a specific movie by its ID."""
    try:
        response = requests.get(
            f"{MOVIE_BACKEND_URL}/{movie_id}", timeout=TIMEOUT_SECONDS
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
            MOVIE_BACKEND_URL, params=params, timeout=TIMEOUT_SECONDS
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
                    timeout=TIMEOUT_SECONDS,
                )
                watchlist_response.raise_for_status()
                watchlist_status = watchlist_response.json()
                movie["in_watchlist"] = watchlist_status.get(
                    "in_watchlist", False
                )
            except Exception as e:
                logger.error(f"Error checking watchlist status: {e}")
                movie["in_watchlist"] = False
        return movie
    except requests.RequestException as e:
        logger.error(f"Error checking movie existence: {e}")
        return None


def get_unique_types():
    """Get unique types (Movie, TV Show, etc.) from the database."""
    try:
        # First try to get types directly from the API
        try:
            response = requests.get(
                f"{MOVIE_BACKEND_URL}/types", timeout=TIMEOUT_SECONDS
            )
            if response.status_code == 200:
                return response.json().get("types", [])
        except requests.RequestException as e:
            logger.warning(f"Could not fetch types from API: {e}")
        # If API doesn't support types endpoint, try to infer from data
        response = requests.get(
            MOVIE_BACKEND_URL,
            params={
                "per_page": 1000
            },  # Get a large sample to find different types
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        movies = data.get("movies", [])
        # Extract unique types
        types = set()
        for movie in movies:
            if movie.get("type"):
                types.add(movie["type"])
        logger.info(f"Found these unique types in the database: {types}")
        return sorted(list(types))
    except Exception as e:
        logger.error(f"Error fetching unique types: {e}")
        return ["Movie", "TV Show"]  # Default fallback
