"""Database and API configuration module."""

import requests
import logging
from supabase import create_client, Client

# Set up logging
logger = logging.getLogger(__name__)

# Supabase credentials
SUPABASE_URL = "https://euibanwordbygkxadvrx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1aWJhbndvcmRieWdreGFkdnJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkzNjM2NDcsImV4cCI6MjA1NDkzOTY0N30.E5AeoS2-6vCHnt1PqsGAtMnaBB8xR48D8XhJ4jvwoEk"

# Movies API URL
MOVIES_API_URL = "http://sse-movies-project2.emdke0g3fbhkfrgy.uksouth.azurecontainer.io/movies"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_movies(query_params=None):
    """
    Fetches movies from the Azure API.
    """
    try:
        params = query_params or {'page': 1, 'per_page': 1000}
        response = requests.get(MOVIES_API_URL, params=params)
        response.raise_for_status()
        return response.json().get("movies", [])
    except requests.RequestException as e:
        logger.error(f"Error fetching movies: {e}")
        return []

def get_unique_categories():
    """
    Fetches and extracts unique categories from movies.
    """
    try:
        # Fetch a sample of movies to extract categories
        response = requests.get(f"{MOVIES_API_URL}?page=1&per_page=1000")
        response.raise_for_status()
        data = response.json()

        # Debug logging
        logger.info(f"API Response: {str(data)[:200]}...")  # First 200 chars

        movies = data.get("movies", [])
        if movies:
            logger.info(f"Sample movie: {movies[0]}")

        categories = set()
        for movie in movies:
            # Try both possible field names
            categories_str = movie.get("listed_in") or movie.get("listedIn") or ""
            logger.info(f"Categories string: {categories_str}")

            for category in categories_str.split(","):
                clean_cat = category.strip()
                if clean_cat:
                    categories.add(clean_cat)

        sorted_cats = sorted(categories)
        logger.info(f"Found categories: {sorted_cats}")
        return sorted_cats

    except Exception as e:
        logger.error(f"Error in get_unique_categories: {e}")
        logger.exception("Full traceback:")
        return []


def add_to_watchlist(username, showId):
    """
    Adds a movie to the user's watchlist in Supabase.
    """
    try:
        data = {"username": username, "showId": showId}
        response = supabase.table("watchlist").insert(data).execute()

        if response.data:
            return True
        else:
            logger.error(f"Error adding to watchlist: {response.error}")
            return False
    except Exception as e:
        logger.error(f"Error in add_to_watchlist: {e}")
        return False


def remove_from_watchlist(username, showId):
    """
    Removes a movie from the user's watchlist.
    """
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
    """
    Fetches all movies in a user's watchlist.
    """
    try:
        response = (
            supabase.table("watchlist")
            .select("showId")
            .eq("username", username)
            .execute()
        )
        return {entry["showId"] for entry in response.data} if response.data else set()
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        return set()
