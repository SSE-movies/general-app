"""Watchlist blueprint for managing user movie watchlists."""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)
from .database import supabase, MOVIES_API_URL
from .decorators import login_required
import requests

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/my_watchlist")
@login_required
def my_watchlist():
    try:
        username = session.get("username")

        # Get watchlist entries from Supabase
        watchlist_entries = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)
            .execute()
            .data
        )
        print(f"Watchlist entries for {username}: {watchlist_entries}")

        # Get all movies from Azure API
        response = requests.get(f"{MOVIES_API_URL}?page=1&per_page=1000")
        response.raise_for_status()
        all_movies = response.json().get("movies", [])

        print(f"Total movies from API: {len(all_movies)}")

        # Create a dictionary for quick lookup of watched status
        watched_dict = {
            entry["showId"]: entry.get("watched", False)
            for entry in watchlist_entries
        }
        print(f"Watched dict: {watched_dict}")

        # Filter and process movies that are in the watchlist
        # Normalize movie data before filtering
        for movie in all_movies:
            if "show_id" in movie:
                movie["showId"] = movie.pop(
                    "show_id"
                )  # Convert to match DB format

        # Now filter movies correctly
        movies_data = []
        for movie in all_movies:
            if movie["showId"] in watched_dict:
                movie["watched"] = watched_dict[movie["showId"]]
                movies_data.append(movie)

        print(f"Filtered movies in watchlist: {movies_data}")

        return render_template(
            "my_watchlist.html", username=username, movies=movies_data
        )

    except Exception as e:
        print(f"Error retrieving watchlist: {e}")
        return render_template(
            "my_watchlist.html",
            username=username,
            movies=[],
            error="Error retrieving watchlist",
        )


@watchlist_bp.route("/add_to_watchlist", methods=["POST"])
@login_required
def add_to_watchlist():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(request.referrer or url_for("search.index"))

        username = session.get("username")

        # Check if already in watchlist
        existing_entry = (
            supabase.table("watchlist")
            .select("*")
            .eq("username", username)
            .eq("showId", show_id)
            .execute()
        )

        if not existing_entry.data:
            # Add to watchlist
            supabase.table("watchlist").insert(
                {"username": username, "showId": show_id, "watched": False}
            ).execute()

        # Return to previous page
        return redirect(request.referrer or url_for("search.index"))

    except Exception as e:
        print(f"Error adding to watchlist: {e}")
        return redirect(request.referrer or url_for("search.index"))


@watchlist_bp.route("/remove_from_watchlist", methods=["POST"])
@login_required
def remove_from_watchlist():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")

        # Remove from watchlist
        supabase.table("watchlist").delete().eq("username", username).eq(
            "showId", show_id
        ).execute()

        return redirect(url_for("watchlist.my_watchlist"))

    except Exception as e:
        print(f"Error removing from watchlist: {e}")
        return redirect(url_for("watchlist.my_watchlist"))


@watchlist_bp.route("/mark_watched", methods=["POST"])
@login_required
def mark_watched():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")

        # Update watched status
        supabase.table("watchlist").update({"watched": True}).eq(
            "username", username
        ).eq("showId", show_id).execute()

        return redirect(url_for("watchlist.my_watchlist"))

    except Exception as e:
        print(f"Error marking as watched: {e}")
        return redirect(url_for("watchlist.my_watchlist"))


@watchlist_bp.route("/mark_unwatched", methods=["POST"])
@login_required
def mark_unwatched():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")

        # Update watched status
        supabase.table("watchlist").update({"watched": False}).eq(
            "username", username
        ).eq("showId", show_id).execute()

        return redirect(url_for("watchlist.my_watchlist"))

    except Exception as e:
        print(f"Error marking as unwatched: {e}")
        return redirect(url_for("watchlist.my_watchlist"))
