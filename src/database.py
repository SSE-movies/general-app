"""Supabase database client configuration module."""

from supabase import create_client, Client
import requests

# Hardcoded Supabase credentials
SUPABASE_URL = "https://euibanwordbygkxadvrx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1aWJhbndvcmRieWdreGFkdnJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkzNjM2NDcsImV4cCI6MjA1NDkzOTY0N30.E5AeoS2-6vCHnt1PqsGAtMnaBB8xR48D8XhJ4jvwoEk"

# Movies API URL
MOVIES_API_URL = "http://sse-movies-project2.emdke0g3fbhkfrgy.uksouth.azurecontainer.io/movies"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_unique_categories():
    """
    Retrieve unique movie categories from the database.

    Returns:
        list: A list of unique movie categories
    """
    try:
        # Fetch movies and extract unique categories
        movies_response = (
            supabase.table("movies").select("listed_in").execute()
        )

        # Extract and clean up categories
        all_categories = []
        for movie in movies_response.data:
            if movie.get("listed_in"):
                # Split categories and strip whitespace
                categories = [
                    cat.strip() for cat in movie["listed_in"].split(",")
                ]
                all_categories.extend(categories)

        # Remove duplicates and sort
        return sorted(set(all_categories))
    except Exception as e:
        print(f"Error fetching unique categories: {e}")
        return []
