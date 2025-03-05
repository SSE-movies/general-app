"""Blueprint for handling movie recommendations using the Generative AI API."""

import json
import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from flask import Blueprint, render_template, session
from google import genai
from google.genai import types

from .database import get_watchlist_movies, check_movie_exists_by_title
from .decorators import login_required


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


recommendations_bp = Blueprint(
    "recommendations", __name__, url_prefix="/recommendations"
)


# Create the client with your API key.
client = genai.Client(api_key=GEMINI_API_KEY)


def strip_markdown(text):
    """Strip markdown formatting if the response is wrapped in triple backticks."""
    if text.startswith("```json"):
        text = text[len("```json") :].strip()
    elif text.startswith("```"):
        text = text[len("```") :].strip()
    if text.endswith("```"):
        text = text[: -len("```")].strip()
    return text


def check_movie_exists(title, username):
    """Check if a movie exists in the database and get its details."""
    print(f"\nChecking movie: {title}")
    matching_movie = check_movie_exists_by_title(title, username)
    if matching_movie:
        print(f"Found match: {matching_movie['title']}")
    else:
        print(f"No match found for {title}")
    return matching_movie


@recommendations_bp.route("", methods=["GET"])
@login_required
def recommendations():
    """Generate a JSON array of 3 movie recommendations using a Generative AI model."""
    username = session.get("username")

    try:
        # Get watchlist movies in parallel with Gemini API call
        with ThreadPoolExecutor(max_workers=2) as executor:
            watchlist_future = executor.submit(get_watchlist_movies, username)

            # Build prompt for Gemini
            movies_data = watchlist_future.result()
            if movies_data:
                movies_list = "; ".join(
                    f"{movie['title']} ({movie.get('listedIn', 'Genre unknown')})"
                    for movie in movies_data
                )
                prompt = (
                    f"Based on the movies in my watchlist: {movies_list}. "
                    "Provide a JSON array of 3 movie recommendations that are "
                    "similar in genre or style to these movies. "
                    "Each recommendation should include the following fields: "
                    "title, listedIn, releaseYear, type ('Movie' or 'TV Show'), "
                    "description, showId, and in_watchlist=False. "
                    "Return only the JSON array without any additional text "
                    "or markdown formatting. Ensure the response is valid JSON."
                )
            else:
                prompt = (
                    "Provide a JSON array of 3 movie recommendations. "
                    "Each recommendation should include the following fields: "
                    "title, listedIn, releaseYear, type ('Movie' or 'TV Show'), "
                    "description, showId, and in_watchlist=False. "
                    "Return only the JSON array without any additional text "
                    "or markdown formatting. Ensure the response is valid JSON."
                )

            # Generate recommendations in parallel with watchlist fetch
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                ),
            )

        raw_text = response.text.strip()
        raw_text = strip_markdown(raw_text)

        if not raw_text:
            raise ValueError("Empty response from the Generative AI model.")

        recommendations_json = json.loads(raw_text)
        print(
            f"\nGot recommendations: {[r['title'] for r in recommendations_json]}"
        )

        # Create a set of watchlist titles for O(1) lookup
        watchlist_titles = {movie["title"].lower() for movie in movies_data}
        print(f"Watchlist titles: {watchlist_titles}")

        # Check all recommendations in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks first
            futures = []
            for rec in recommendations_json:
                if "showId" in rec:
                    del rec["showId"]
                future = executor.submit(
                    check_movie_exists, rec["title"], username
                )
                futures.append((future, rec))

            # Process results as they complete
            for future, recommendation in futures:
                try:
                    matching_movie = future.result()
                    print(f"\nProcessing result for {recommendation['title']}")
                    if matching_movie:
                        print(
                            f"Found matching movie: {matching_movie['title']}"
                        )
                        recommendation["exists_in_database"] = True
                        recommendation["showId"] = matching_movie["showId"]
                        recommendation["releaseYear"] = matching_movie[
                            "releaseYear"
                        ]
                        recommendation["in_watchlist"] = matching_movie.get(
                            "in_watchlist", False
                        )
                        print(
                            f"Set exists_in_database=True for {recommendation['title']}"
                        )
                    else:
                        print(f"No match found for {recommendation['title']}")
                        recommendation["exists_in_database"] = False
                        recommendation["in_watchlist"] = False
                except Exception as e:
                    print(
                        f"Error checking movie {recommendation['title']}: {e}"
                    )
                    recommendation["exists_in_database"] = False
                    recommendation["in_watchlist"] = False

    except Exception as e:
        recommendations_json = []
        print("Error generating recommendations:", e)

    return render_template(
        "recommendations.html", recommendations=recommendations_json
    )
