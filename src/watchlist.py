"""Watchlist blueprint for managing user movie watchlists."""
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)
from .database import supabase
from .decorators import login_required

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/add_to_watchlist", methods=["POST"])
@login_required
def add_to_watchlist():
    """
    Add a movie to the user's watchlist.

    Handles both JSON and form data requests.
    Returns a JSON response indicating success or failure.
    """
    try:
        if request.is_json:
            data = request.get_json()
            show_id = data.get("showId")
        else:
            show_id = request.form.get("showId")

        if not show_id:
            return jsonify({"error": "No show ID provided"}), 400

        username = session.get("username")

        existing_entry = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)
            .eq("showId", show_id)
            .execute()
        )

        if existing_entry.data:
            return jsonify({"message": "Already in watchlist"}), 200

        supabase.table("watchlist").insert(
            {"username": username, "showId": show_id}
        ).execute()

        return jsonify({"message": "Successfully added to watchlist"}), 200

    except Exception as e:
        # More specific error handling would be better
        print(f"Error adding movie to watchlist: {e}")
        return jsonify({"error": "Internal server error"}), 500


@watchlist_bp.route("/my_watchlist")
@login_required
def view_watchlist():
    """
    Retrieve and display the user's watchlist.

    Fetches watchlist entries and corresponding movie details.
    Renders the watchlist template with movie information.
    """
    try:
        username = session.get("username")

        watchlist_entries = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)
            .execute()
            .data
        )

        show_ids = (
            [entry["showId"] for entry in watchlist_entries]
            if watchlist_entries
            else []
        )

        # Fetch movie details for watchlist entries
        movies_data = (
            supabase.table("movies")
            .select("*")
            .in_("showId", show_ids)
            .execute()
            .data if show_ids else []
        )

        # Create a dictionary of watched status
        watched_dict = {
            entry["showId"]: entry.get("watched", False)
            for entry in watchlist_entries
        }

        # Add watched status to movie data
        for movie in movies_data:
            movie["watched"] = watched_dict.get(movie["showId"], False)

        return render_template(
            "my_watchlist.html", username=username, movies=movies_data
        )

    except Exception as e:
        # More specific error handling would be better
        print(f"Error retrieving watchlist: {e}")
        return "Error retrieving watchlist", 500


@watchlist_bp.route("/remove_from_watchlist", methods=["POST"])
@login_required
def remove_from_watchlist():
    """
    Remove a movie from the user's watchlist.

    Redirects back to the watchlist view after removal.
    """
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.view_watchlist"))

        username = session.get("username")

        # Check if entry exists before attempting to delete
        existing_entry = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)
            .eq("showId", show_id)
            .execute()
        )

        if not existing_entry.data:
            return redirect(url_for("watchlist.view_watchlist"))

        # Delete the specific watchlist entry
        supabase.table("watchlist").delete().eq("username", username).eq(
            "showId", show_id
        ).execute()

        return redirect(url_for("watchlist.view_watchlist"))

    except Exception as e:
        # Log the error, but don't expose details to the user
        print(f"Error removing movie from watchlist: {e}")
        return redirect(url_for("watchlist.view_watchlist"))


@watchlist_bp.route("/mark_watched", methods=["POST"])
@login_required
def mark_watched():
    """
    Mark a movie in the watchlist as watched.

    Redirects back to the watchlist view after updating.
    """
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.view_watchlist"))

        username = session.get("username")

        supabase.table("watchlist").update({"watched": True}).eq(
            "username", username
        ).eq("showId", show_id).execute()

        return redirect(url_for("watchlist.view_watchlist"))

    except Exception as e:
        # Log the error, but don't expose details to the user
        print(f"Error marking movie as watched: {e}")
        return redirect(url_for("watchlist.view_watchlist"))


@watchlist_bp.route("/mark_unwatched", methods=["POST"])
@login_required
def mark_unwatched():
    """
    Mark a movie in the watchlist as unwatched.

    Redirects back to the watchlist view after updating.
    """
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.view_watchlist"))

        username = session.get("username")

        supabase.table("watchlist").update({"watched": False}).eq(
            "username", username
        ).eq("showId", show_id).execute()

        return redirect(url_for("watchlist.view_watchlist"))

    except Exception as e:
        # Log the error, but don't expose details to the user
        print(f"Error marking movie as unwatched: {e}")
        return redirect(url_for("watchlist.view_watchlist"))