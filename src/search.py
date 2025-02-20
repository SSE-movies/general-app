from flask import Blueprint, render_template, request, session
import requests
from .database import supabase, get_unique_categories, MOVIES_API_URL
from .decorators import login_required

search_bp = Blueprint('search', __name__)

@search_bp.route("/search", methods=["GET", "POST"])
@login_required
def index():
    try:
        response = requests.get(f"{MOVIES_API_URL}?page=1&per_page=1000")
        response.raise_for_status()
        movies_data = response.json().get("movies", [])
    except requests.RequestException as e:
        print(f"Error fetching movies: {e}")
        movies_data = []

    categories = get_unique_categories()

    if request.method == "POST":
        search_data = request.form
        selected_categories = request.form.getlist("categories")
    else:
        search_data = request.args
        selected_categories = request.args.getlist("categories")

    filtered_movies = []
    for movie in movies_data:
        if any(cat.strip() in movie["listedIn"] for cat in selected_categories):
            filtered_movies.append(movie)

    return render_template(
        "search.html",
        username=session.get("username"),
        movies=filtered_movies,
        categories=categories,
    )

@search_bp.route("/results", methods=["GET"])
@login_required
def results():
    title_query = request.args.get("title", "")
    type_query = request.args.get("type", "")
    selected_categories = request.args.getlist("categories")
    release_year = request.args.get("release_year", "")

    query_params = {}

    if title_query:
        query_params["title"] = title_query
    if type_query:
        query_params["type"] = type_query
    if selected_categories:
        query_params["categories"] = ",".join(selected_categories)
    if release_year:
        query_params["release_year"] = release_year

    try:
        print("DEBUG: Query Params being sent to API:", query_params)
        response = requests.get(MOVIES_API_URL, params=query_params)
        response.raise_for_status()
        movies_data = response.json().get("movies", [])
    except requests.RequestException as e:
        print(f"Error fetching movies: {e}")
        movies_data = []

    categories = get_unique_categories()

    return render_template(
        "results.html",
        username=session.get("username"),
        movies=movies_data,
        categories=categories,
    )