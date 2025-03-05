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

logger.debug(f"MOVIES_API_URL: {MOVIES_API_URL}")

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


def get_filtered_movies(query_params=None, username=None):
    """
    Fetches and filters movies based on search criteria.
    Marks watchlist status if username is provided.
    Passes pagination parameters to the API so that only 10 movies are fetched at a time.
    """
    try:
        # Build query params
        params = {}
        if query_params:
            if query_params.get("title"):
                params["title"] = query_params["title"]
            if query_params.get("type"):
                params["type"] = query_params["type"]
            if query_params.get("categories"):
                params["categories"] = query_params["categories"]
            if query_params.get("release_year"):
                params["release_year"] = query_params["release_year"]

        # Add pagination parameters to the API request
        page = request.args.get("page", 1, type=int)
        results_per_page = 10
        params["page"] = page
        params["per_page"] = results_per_page

        # Fetch filtered movies
        response = requests.get(
            MOVIES_API_URL, params=params, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        movies = data.get("movies", [])

        # Get user's watchlist if username provided
        watchlist_movies = set()
        if username:
            watchlist = get_watchlist(username)
            watchlist_movies = {entry["showId"] for entry in watchlist}

        # Normalise field names and add watchlist status
        for movie in movies:
            if "listed_in" in movie:
                movie["listedIn"] = movie.pop("listed_in")
            if "show_id" in movie:
                movie["showId"] = movie.pop("show_id")
            if "release_year" in movie:
                movie["releaseYear"] = movie.pop("release_year")
            movie["in_watchlist"] = movie["showId"] in watchlist_movies

        # Determine pagination flags
        has_next = (
            len(movies) == results_per_page
        )  # assume a next page if full page was returned
        has_prev = page > 1

        # Don't return total for now
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


def add_to_watchlist(username, showId):
    """Adds a movie to the user's watchlist in Supabase."""
    try:
        # Check only this user's watchlist
        existing = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)  # Filter for this user first
            .eq("showId", showId)  # Then check for this specific movie
            .execute()
        )

        if not existing.data:
            data = {"username": username, "showId": showId, "watched": False}
            response = supabase.table("watchlist").insert(data).execute()
            return True if response.data else False
        return True
    except Exception as e:
        logger.error(f"Error in add_to_watchlist: {e}")
        return False


def remove_from_watchlist(username, showId):
    """Removes a movie from the user's watchlist."""
    try:
        response = (
            supabase.table("watchlist")
            .delete()
            .eq("username", username)
            .eq("showId", showId)
            .execute()
        )
        return True if response.data else False
    except Exception as e:
        logger.error(f"Error in remove_from_watchlist: {e}")
        return False


def get_watchlist(username):
    """Fetches all movies in a user's watchlist."""
    try:
        response = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        return []


def get_movies_by_ids(show_ids):
    """Get specific movies by their IDs."""
    try:
        # Convert list of IDs to comma-separated string
        ids_string = ",".join(show_ids)
        
        # Request movies with these IDs
        params = {
            "show_ids": ids_string,
            "per_page": len(show_ids)  # Make sure we get all requested movies
        }
        response = requests.get(MOVIES_API_URL, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        movies = response.json().get("movies", [])
        
        # Normalize the keys
        for movie in movies:
            if "listed_in" in movie:
                movie["listedIn"] = movie.pop("listed_in")
            if "show_id" in movie:
                movie["showId"] = movie.pop("show_id")
            if "release_year" in movie:
                movie["releaseYear"] = movie.pop("release_year")
                
        return movies
    except requests.RequestException as e:
        logger.error(f"Error fetching movies by IDs: {e}")
        return []


def get_watchlist_movies(username):
    """
    Retrieve movies that are in the user's watchlist.
    Normalizes keys and attaches the watched status.
    """
    watchlist_entries = get_watchlist(username)
    
    if not watchlist_entries:
        return []
        
    # Get the showIds from watchlist
    show_ids = [entry["showId"] for entry in watchlist_entries]
    
    # Get all the movies that are in the watchlist
    movies = get_movies_by_ids(show_ids)
    
    # Build a lookup for the watched status
    watched_dict = {
        entry["showId"]: entry.get("watched", False)
        for entry in watchlist_entries
    }
    
    # Attach watched status to each movie
    for movie in movies:
        movie["watched"] = watched_dict.get(movie["showId"], False)
    
    return movies


def update_watched_status(username, showId, watched):
    """Updates the watched status of a movie in the watchlist."""
    try:
        response = (
            supabase.table("watchlist")
            .update({"watched": watched})
            .eq("username", username)
            .eq("showId", showId)
            .execute()
        )
        return True if response.data else False
    except Exception as e:
        logger.error(f"Error updating watched status: {e}")
        return False


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
            watchlist = get_watchlist(username)
            watchlist_movies = {entry["showId"] for entry in watchlist}
            movie["in_watchlist"] = movie["showId"] in watchlist_movies

        return movie

    except requests.RequestException as e:
        logger.error(f"Error checking movie existence: {e}")
        return None
