from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)
from functools import wraps
import os
from supabase import create_client, Client
import requests
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="src/templates", static_folder="src/static")

# Fetching movie API
MOVIES_API_URL = (
    "http://sse-movies-project2.emdke0g3fbhkfrgy.uksouth.azurecontainer.io/movies"
)
# MOVIES_API_URL = "http://127.0.0.1:81/movies"

# Configuration
app.config["SECRET_KEY"] = os.urandom(24)

# Initialize Supabase client
supabase: Client = create_client(
    "https://euibanwordbygkxadvrx.supabase.co",
    (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1aWJh"
    "bndvcmRieWdreGFkdnJ4Iiwicm9sZSI6ImFub24i"
    "LCJpYXQiOjE3MzkzNjM2NDcsImV4cCI6MjA1NDkz"
    "OTY0N30.E5AeoS2-6vCHnt1PqsGAtMnaBB8xR48D8"
    "XhJ4jvwoEk"
    )
)


def get_unique_categories():
    """
    Fetches all 'listedIn' strings from the 'movies' table in Supabase,
    splits them by commas, and returns a sorted list of unique categories.
    """
    try:
        # Query the 'movies' table for the 'listedIn' column
        response = supabase.table("movies").select("listedIn").execute()
        rows = (
            response.data
        )  # Each row is a dict, e.g. {"listedIn": "Documentaries, International Movies"}

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


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    return render_template("index.html", show_navbar=False)


@app.route("/login", methods=["GET", "POST"])
def login():
    success = request.args.get("success")
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            # Get user from database
            user_response = (
                supabase.table("profiles")
                .select("*")
                .eq("username", username)
                .execute()
            )

            if not user_response.data:
                return render_template(
                    "login.html",
                    show_navbar=False,
                    error="Invalid credentials",
                )

            user_data = user_response.data[0]

            # Verify password
            if bcrypt.checkpw(
                password.encode("utf-8"), user_data["password"].encode("utf-8")
            ):
                # Store user info in session
                session["user_id"] = user_data["id"]
                session["username"] = user_data["username"]
                session["is_admin"] = user_data["is_admin"]

                if user_data["is_admin"]:
                    return redirect(url_for("admin"))
                return redirect(url_for("search"))
            else:
                return render_template(
                    "login.html",
                    show_navbar=False,
                    error="Invalid credentials",
                )

        except Exception as e:
            print(f"Login error: {e}")
            return render_template(
                "login.html", show_navbar=False, error="Invalid credentials"
            )

    return render_template("login.html", show_navbar=False, success=success)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            if not username or not password:
                return render_template(
                    "register.html",
                    show_navbar=False,
                    error="Username and password are required",
                )

            # Check if username already exists
            existing_user = (
                supabase.table("profiles")
                .select("username")
                .eq("username", username)
                .execute()
            )
            if existing_user.data:
                return render_template(
                    "register.html",
                    show_navbar=False,
                    error="Username already exists",
                )

            # Hash the password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

            # Create profile entry
            profile_data = {
                "username": username,
                "password": hashed_password.decode("utf-8"),
                "is_admin": False,
            }

            supabase.table("profiles").insert(profile_data).execute()

            return redirect(
                url_for(
                    "login",
                    success="Registration successful. Please login now.",
                )
            )

        except Exception as e:
            print(f"Registration error: {e}")
            error_message = str(e)
            return render_template(
                "register.html", show_navbar=False, error=error_message
            )

    return render_template(
        "register.html",
        show_navbar=False,
    )


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    try:
        # Fetch all movies (for demo: page=1&per_page=1000)
        response = requests.get(f"{MOVIES_API_URL}?page=1&per_page=1000")
        response.raise_for_status()
        movies_data = response.json().get("movies", [])
    except requests.RequestException as e:
        print(f"Error fetching movies: {e}")
        # If there's an error, we'll default to an empty list
        movies_data = []

    # Get all categories from the database
    categories = get_unique_categories()

    if request.method == "POST":
        search_data = request.form
        selected_categories = request.form.getlist("categories")
    else:
        search_data = request.args
        selected_categories = request.args.getlist("categories")

    # Filter the movies_data based on selected_categories
    filtered_movies = []
    for movie in movies_data:
        # movie['listedIn'] is e.g. "Documentaries, International Movies"
        if any(cat.strip() in movie["listedIn"] for cat in selected_categories):
            filtered_movies.append(movie)

    # Render template, passing both the movies and the unique category list
    return render_template(
        "search.html",
        username=session.get("username"),
        movies=filtered_movies,  # Or movies_data if not filtering
        categories=categories,
    )


@app.route("/add_to_watchlist", methods=["POST"])
@login_required
def add_to_watchlist():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("search"))

        # Get username from the session
        username = session.get("username")

        # Check if the movie is already in watchlist
        existing_entry = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)
            .eq("showId", show_id)
            .execute()
        )

        if existing_entry.data:
            # Already in watchlist: redirect (avoids duplication bugs and resubmitting form)
            return redirect(url_for("search"))

        # Insert new watchlist entry
        response = supabase.table("watchlist").insert(
            {"username": username, "showId": show_id}
        ).execute()
        print("Insert response:", response)

        return redirect(url_for("search"))

    except Exception as e:
        print(f"Error adding movie to watchlist: {e}")
        return redirect(url_for("search"))


@app.route("/my_watchlist")
@login_required
def my_watchlist():
    try:
        username = session.get("username")

        # Retrieve watchlist entries for the current user
        watchlist_entries = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)
            .execute()
            .data
        )

        print("--------------1-----------------")

        # Fetch all the movie rows for these showIDs
        show_ids = [entry["showId"] for entry in watchlist_entries] if watchlist_entries else []
        if show_ids:
            movies_response = (
                supabase.table("movies")
                .select("*")
                .in_("showId", show_ids)
                .execute()
            )
            movies_data = movies_response.data
        else:
            movies_data = []

        print("--------------2-----------------")

        # Create a dictionary mapping showIDs to show details
        movies_dict = {m["showId"]: m for m in movies_data}

        # Merge each watchlist entry with its corresponding info
        combined_entries = []
        for wl_entry in watchlist_entries:
            show_id = wl_entry["showId"]
            # If there's a matching movie in the dictionary, merge them:
            if show_id in movies_dict:
                movie_info = movies_dict[show_id]
                # Merge them into a single dict so you have both .title and .watched
                combined_entry = {**movie_info, **wl_entry}
                combined_entries.append(combined_entry)

        print("--------------3-----------------")

        # Render the watchlist page with movie details
        return render_template(
            "my_watchlist.html",
            username=username,
            movies=combined_entries
        )

    except Exception as e:
        print(f"Error retrieving watchlist: {e}")
        return "Error retrieving watchlist", 500


@app.route("/remove_from_watchlist", methods=["POST"])
@login_required
def remove_from_watchlist():
    try:
        # Retrieve the showID from the form data
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("my_watchlist"))

        # Get the username from the session
        username = session.get("username")
        # Delete the watchlist entry for this user
        supabase.table("watchlist").delete().eq("username", username).eq(
            "showId", show_id
        ).execute()

        # Redirect to the watchlist page after deletion
        return redirect(url_for("my_watchlist"))
    except Exception as e:
        print(f"Error removing movie from watchlist: {e}")
        return redirect(url_for("my_watchlist"))


@app.route("/mark_watched", methods=["POST"])
@login_required
def mark_watched():
    try:
        # Retrieve the showID from the form data
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("my_watchlist"))

        # Get the username from the session
        username = session.get("username")
        # Update the watchlist entry
        supabase.table("watchlist").update({"watched": True}).eq(
            "username", username
        ).eq("showId", show_id).execute()

        # Redirect to the watchlist page after database is updated
        return redirect(url_for("my_watchlist"))

    except Exception as e:
        print(f"Error marking movie as watched: {e}")
        return redirect(url_for("my_watchlist"))


@app.route("/mark_unwatched", methods=["POST"])
@login_required
def mark_unwatched():
    try:
        # Retrieve the showID from the form data
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("my_watchlist"))

        # Get the username from the session
        username = session.get("username")
        # Update the watchlist entry
        supabase.table("watchlist").update({"watched": False}).eq(
            "username", username
        ).eq("showId", show_id).execute()

        # Redirect to the watchlist page after database is updated
        return redirect(url_for("my_watchlist"))

    except Exception as e:
        print(f"Error marking movie as unwatched: {e}")
        return redirect(url_for("my_watchlist"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin():
    try:
        response = supabase.table("profiles").select("*").execute()
        users = response.data
        return render_template(
            "admin.html", username=session.get("username"), users=users
        )
    except Exception as e:
        print(f"Admin page error: {e}")
        return "Error loading admin page", 500


@app.route("/api/users")
@admin_required
def get_users():
    try:
        response = supabase.table("profiles").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<user_id>/reset-password", methods=["POST"])
@admin_required
def reset_password(user_id):
    try:
        new_password = request.json.get("newPassword")
        if not new_password:
            return jsonify({"error": "New password is required"}), 400

        # Hash the new password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), salt)

        # Update user's password in Supabase
        supabase.table("profiles").update(
            {"password": hashed_password.decode("utf-8")}
        ).eq("id", user_id).execute()

        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<user_id>/username", methods=["PUT"])
@admin_required
def update_username(user_id):
    try:
        new_username = request.json.get("newUsername")
        if not new_username:
            return jsonify({"error": "New username is required"}), 400

        # Update username in profiles table
        supabase.table("profiles").update({"username": new_username}).eq(
            "id", user_id
        ).execute()

        return jsonify({"message": "Username updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    try:
        # Delete user from profiles
        supabase.table("profiles").delete().eq("id", user_id).execute()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results", methods=["GET"])
@login_required
def results():
    """
    Renders a results page displaying movies after the user searches on /search.
    The GET parameters for title, type, categories, and release_year are picked up here.
    """
    title_query = request.args.get("title", "")
    type_query = request.args.get("type", "")
    selected_categories = request.args.getlist("categories")
    release_year = request.args.get("release_year", "")

    # Build query params for the external SSE Movie API (or Supabase).
    # Adjust this to match your backend's actual query conventions.
    query_params = {}

    if title_query:
        query_params["title"] = title_query
    if type_query:
        query_params["type"] = type_query
    if selected_categories:
        # e.g. for the SSE Movie API, categories can be passed as a comma-separated string
        query_params["categories"] = ",".join(selected_categories)
    if release_year:
        query_params["release_year"] = release_year

    try:
        # Debugging to be deleted
        print("DEBUG: Query Params being sent to API:", query_params)
        # Query the SSE Movie API with the built params
        response = requests.get(MOVIES_API_URL, params=query_params)
        response.raise_for_status()
        movies_data = response.json().get("movies", [])
    except requests.RequestException as e:
        print(f"Error fetching movies: {e}")

        movies_data = []

    # You could also re-fetch categories if you want to show them in the results page, but optional
    categories = get_unique_categories()

    return render_template(
        "results.html",
        username=session.get("username"),
        movies=movies_data,
        categories=categories,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
