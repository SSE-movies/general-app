"""Database configuration and client setup module."""
from supabase import create_client, Client

# Initialize Supabase client
supabase: Client = create_client(
    "https://euibanwordbygkxadvrx.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1aWJhbndvcmRieWdreGFkdnJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkzNjM2NDcsImV4cCI6MjA1NDkzOTY0N30.E5AeoS2-6vCHnt1PqsGAtMnaBB8xR48D8XhJ4jvwoEk",
)

MOVIES_API_URL = "http://sse-movies-project2.emdke0g3fbhkfrgy.uksouth.azurecontainer.io/movies"


def get_unique_categories():
    """
    Fetches all 'listedIn' strings from the 'movies' table in Supabase,
    splits them by commas, and returns a sorted list of unique categories.
    """
    try:
        # Query the 'movies' table for the 'listedIn' column
        response = supabase.table("movies").select("listedIn").execute()
        rows = response.data

        categories = set()
        if rows:
            for row in rows:
                listed_in_str = row.get("listedIn", "")
                # Split by comma, strip extra whitespace
                for cat in listed_in_str.split(","):
                    cat = cat.strip()
                    if cat:
                        categories.add(cat)

        return sorted(categories)
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []
