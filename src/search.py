"""Search Blueprint - Handles movie search and filtering."""

import logging
from flask import Blueprint, render_template, request, session
from .database import get_unique_categories, get_filtered_movies
from .decorators import login_required

logger = logging.getLogger(__name__)

search_bp = Blueprint("search", __name__)


@search_bp.route("/search", methods=["GET", "POST"])
@login_required
def index():
    """Displays the search page and filters."""
    try:
        categories = get_unique_categories()
        return render_template(
            "search.html",
            username=session.get("username"),
            categories=categories,
        )
    except Exception as e:
        logger.error(f"Error loading search page: {e}")
        return render_template(
            "search.html",
            username=session.get("username"),
            categories=[],
            error="Failed to load categories",
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

    """Shows filtered search results."""
    try:
        # Get search parameters
        query_params = {
            "title": request.args.get("title", ""),
            "type": request.args.get("type", ""),
            "categories": ",".join(request.args.getlist("categories")),
            "release_year": request.args.get("release_year", ""),
        }

        # Get username for watchlist status
        username = session.get("username")

        # Get filtered movies with watchlist status
        movies = get_filtered_movies(query_params, username)
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
            "results.html", username=username, movies=movies
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
