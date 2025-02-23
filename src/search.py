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

    """ Shows filtered search results with pagination. """
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
        movies, page, has_next, has_prev, total = get_filtered_movies(query_params, username)

        return render_template(
            "results.html",
            username=username,
            movies=movies,
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
