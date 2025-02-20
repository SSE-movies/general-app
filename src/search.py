"""
Search Blueprint - Handles movie search and filtering.
"""

import logging
import requests
from flask import Blueprint, render_template, request, session, flash
from .database import supabase, get_unique_categories, MOVIES_API_URL
from .decorators import login_required

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

search_bp = Blueprint("search", __name__)


@search_bp.route("/search", methods=["GET", "POST"])
@login_required
def index():
    """
    Displays the search page and fetches movies based on user-selected filters.
    """
    selected_categories = (
        request.form.getlist("categories")
        if request.method == "POST"
        else request.args.getlist("categories")
    )

    movies_data = []  # Default to empty list (no movies shown by default)

    if selected_categories:  # Fetch movies only if categories are selected
        query_params = {
            "page": 1,
            "per_page": 100,
            "categories": ",".join(selected_categories),
        }

        try:
            response = requests.get(MOVIES_API_URL, params=query_params)
            response.raise_for_status()
            movies_data = response.json().get("movies", [])
        except requests.RequestException as e:
            logger.error(f"Error fetching movies: {e}")
            flash("Failed to fetch movies. Please try again later.", "danger")

    categories = get_unique_categories()

    return render_template(
        "search.html",
        username=session.get("username"),
        movies=movies_data,  # Will be empty unless filters are applied
        categories=categories,
    )


@search_bp.route("/results", methods=["GET"])
@login_required
def results():
    """
    Handles filtering movies based on search parameters.
    """
    query_params = {
        key: request.args.get(key)
        for key in ["title", "type", "release_year"]
        if request.args.get(key)
    }
    selected_categories = request.args.getlist("categories")

    if selected_categories:
        query_params["categories"] = ",".join(selected_categories)

    try:
        logger.info(f"Querying API with params: {query_params}")
        response = requests.get(MOVIES_API_URL, params=query_params)
        response.raise_for_status()
        movies_data = response.json().get("movies", [])
    except requests.RequestException as e:
        logger.error(f"Error fetching movies: {e}")
        flash(
            "Error retrieving search results. Please try again later.",
            "danger",
        )
        movies_data = []

    categories = get_unique_categories()

    return render_template(
        "results.html",
        username=session.get("username"),
        movies=movies_data,
        categories=categories,
    )
