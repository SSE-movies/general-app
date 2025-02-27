"""Database and API configuration module."""

import os
import requests
import logging
from flask import request
from supabase import create_client, Client

# Set up logging
logger = logging.getLogger(__name__)

# Get configuration from environment
MOVIES_API_URL = os.environ.get('MOVIES_API_URL')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

logger.debug(f"MOVIES_API_URL: {MOVIES_API_URL}")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_movies():
    """Get all movies for initial loading."""
    try:
        response = requests.get(MOVIES_API_URL)
        response.raise_for_status()
        return response.json().get("movies", [])
    except requests.RequestException as e:
        logger.error(f"Error fetching movies: {e}")
        return []


def get_filtered_movies(query_params=None, username=None):
    """
    Fetches and filters movies based on search criteria.
    Also marks watchlist status if username is provided.
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

        # Fetch filtered movies
        response = requests.get(MOVIES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        movies = data.get("movies", [])

        # Get user's watchlist if username provided
        watchlist_movies = set()
        if username:
            watchlist = get_watchlist(username)
            watchlist_movies = {entry["showId"] for entry in watchlist}

        # Normalize field names and add watchlist status
        for movie in movies:
            if "listed_in" in movie:
                movie["listedIn"] = movie.pop("listed_in")
            if "show_id" in movie:
                movie["showId"] = movie.pop("show_id")
            if "release_year" in movie:
                movie["releaseYear"] = movie.pop("release_year")
            movie["in_watchlist"] = movie["showId"] in watchlist_movies

        # Pagination parameters
        total = len(movies)  # Total number of results
        page = request.args.get("page", 1, type=int)
        results_per_page = 10
        offset = (page - 1) * results_per_page

        # Determine if there are next/previous pages
        has_next = (offset + results_per_page) < total
        has_prev = page > 1

        # Slice movies list for the current page
        paginated_movies = movies[offset : (offset + results_per_page)]

        return paginated_movies, page, has_next, has_prev, total

    except requests.RequestException as e:
        logger.error(f"Error fetching filtered movies: {e}")
        return [], 1, False, False, 0


def get_unique_categories():
    """Fetches and extracts unique categories from movies."""
    try:
        response = requests.get(f"{MOVIES_API_URL}?page=1&per_page=1000")
        response.raise_for_status()
        data = response.json()

        movies = data.get("movies", [])
        categories = set()
        for movie in movies:
            categories_str = (
                movie.get("listed_in") or movie.get("listedIn") or ""
            )
            for category in categories_str.split(","):
                clean_cat = category.strip()
                if clean_cat:
                    categories.add(clean_cat)

        return sorted(list(categories))
    except Exception as e:
        logger.error(f"Error in get_unique_categories: {e}")
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
