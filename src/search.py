"""Search Blueprint - Handles movie search and filtering."""

import logging
import requests
from flask import Blueprint, render_template, request, session
from .database import get_unique_categories, MOVIES_API_URL, supabase
from .decorators import login_required

logger = logging.getLogger(__name__)

search_bp = Blueprint("search", __name__)


def get_user_watchlist(username):
    """Get list of movie IDs in user's watchlist."""
    try:
        watchlist = (
            supabase.table("watchlist")
            .select("showId")
            .eq("username", username)
            .execute()
        )
        return {item["showId"] for item in watchlist.data}
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        return set()


@search_bp.route("/search", methods=["GET", "POST"])
@login_required
def index():
    """
    Displays the search page and filters.
    """
    categories = get_unique_categories()
    return render_template(
        "search.html", username=session.get("username"), categories=categories
    )


@search_bp.route("/results", methods=["GET"])
@login_required
def results():
    """
    Shows filtered search results with pagination
    """
    title_query = request.args.get("title", "")
    type_query = request.args.get("type", "")
    selected_categories = request.args.getlist("categories")
    release_year = request.args.get("release_year", "")

    # Pagination parameters
    page = request.args.get("page", 1, type=int)
    results_per_page = 10
    offset = (page - 1) * results_per_page

    try:
        # Get user's watchlist
        username = session.get("username")
        watchlist_movies = get_user_watchlist(username)

        # Build query params
        query_params = {}
        if title_query:
            query_params["title"] = title_query
        if type_query:
            query_params["type"] = type_query
        if selected_categories:
            query_params["categories"] = ",".join(selected_categories)
        if release_year:
            query_params["release_year"] = release_year

        # Add pagination parameters
        query_params["limit"] = results_per_page
        query_params["offset"] = offset

        # Fetch movies
        response = requests.get(MOVIES_API_URL, params=query_params)
        response.raise_for_status()
        data = response.json()
        movies_data = data.get("movies", [])
        total = data.get("total", 0) # Total number of results

        # Transform field names and add watchlist status
        for movie in movies_data:
            if "listed_in" in movie:
                movie["listedIn"] = movie.pop("listed_in")
            if "show_id" in movie:
                movie["showId"] = movie.pop("show_id")
            # Add watchlist status
            movie["in_watchlist"] = movie["showId"] in watchlist_movies

        # Determine if there are next/previous pages
        has_next = offset + results_per_page < total
        has_prev = page > 1

        return render_template(
            "results.html",
            username=username,
            movies=movies_data,
            page=page,
            has_next=has_next,
            has_prev=has_prev,
            total=total,
        )
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        return render_template(
            "results.html",
            username=session.get("username"),
            movies=[],
            error="Failed to fetch results",
        )
