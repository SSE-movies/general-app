"""Watchlist blueprint for managing user movie watchlists."""

import os
import logging
import requests
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)
from .decorators import login_required

# Set up logging
logger = logging.getLogger(__name__)

# Constants
TIMEOUT_SECONDS = 10

# Get configuration from environment
WATCHLIST_BACKEND_URL = os.environ.get("WATCHLIST_BACKEND_URL")

# OLD VERSION - Using Supabase directly
"""
class WatchlistService:
    @staticmethod
    def get_watchlist(username):
        try:
            response = (
                supabase.table("watchlist")
                .select("*")
                .eq("username", username)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            return []

    @staticmethod
    def add_to_watchlist(username, show_id):
        try:
            existing = (
                supabase.table("watchlist")
                .select("*")
                .eq("username", username)
                .eq("showId", show_id)
                .execute()
            )

            if not existing.data:
                data = {"username": username, "showId": show_id, "watched": False}
                response = supabase.table("watchlist").insert(data).execute()
                return True if response.data else False
            return True
        except Exception as e:
            logger.error(f"Error in add_to_watchlist: {e}")
            return False

    @staticmethod
    def remove_from_watchlist(username, show_id):
        try:
            response = (
                supabase.table("watchlist")
                .delete()
                .eq("username", username)
                .eq("showId", show_id)
                .execute()
            )
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error in remove_from_watchlist: {e}")
            return False

    @staticmethod
    def update_watched_status(username, show_id, watched):
        try:
            response = (
                supabase.table("watchlist")
                .update({"watched": watched})
                .eq("username", username)
                .eq("showId", show_id)
                .execute()
            )
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error updating watched status: {e}")
            return False
"""


# NEW VERSION - Using watchlist-backend microservice
class WatchlistService:
    """Service class for interacting with the watchlist backend API.
    This is a thin client that delegates most logic to the backend service."""

    @staticmethod
    def get_watchlist(username):
        """Get all movies in a user's watchlist with full movie details.
        The backend handles fetching and combining watchlist data with movie details.
        """
        try:
            response = requests.get(
                f"{WATCHLIST_BACKEND_URL}/watchlist/{username}",
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json().get("movies", [])
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            return []

    @staticmethod
    def add_to_watchlist(username, show_id):
        """Add a movie to the user's watchlist."""
        try:
            # Ensure show_id is a string
            show_id_str = str(show_id)
            logger.info(
                f"WATCHLIST_BACKEND_URL is set to: {WATCHLIST_BACKEND_URL}"
            )
            logger.info(
                f"Adding to watchlist: username={username}, showId={show_id_str}"
            )

            payload = {"username": username, "showId": show_id_str}
            logger.info(f"Sending payload: {payload}")

            full_url = f"{WATCHLIST_BACKEND_URL}/watchlist"
            logger.info(f"Making POST request to: {full_url}")

            response = requests.post(
                full_url,
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )

            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")

            response.raise_for_status()
            return True
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to watchlist backend: {e}")
            return False
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return False

    @staticmethod
    def remove_from_watchlist(username, show_id):
        """Remove a movie from the user's watchlist.
        The backend handles validation and existence checking."""
        try:
            # Ensure show_id is a string
            show_id_str = str(show_id)
            response = requests.delete(
                f"{WATCHLIST_BACKEND_URL}/watchlist",
                json={"username": username, "showId": show_id_str},
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return False

    @staticmethod
    def update_watched_status(username, show_id, watched):
        """Update the watched status of a movie in the watchlist.
        The backend handles validation and status updates."""
        try:
            # Ensure show_id is a string
            show_id_str = str(show_id)
            response = requests.put(
                f"{WATCHLIST_BACKEND_URL}/watchlist/status",
                json={
                    "username": username,
                    "showId": show_id_str,
                    "watched": watched,
                },
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error updating watched status: {e}")
            return False

    @staticmethod
    def check_watchlist_status(username, show_id):
        """Check if a movie is in the user's watchlist and its status."""
        try:
            # Ensure show_id is a string
            show_id_str = str(show_id)
            response = requests.get(
                f"{WATCHLIST_BACKEND_URL}/watchlist/status/{username}/{show_id_str}",
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error checking watchlist status: {e}")
            return {"in_watchlist": False}

    @staticmethod
    def batch_check_watchlist_status(username, show_ids):
        """Check watchlist status for multiple movies at once.

        Args:
            username (str): The username to check for
            show_ids (list): List of show IDs to check

        Returns:
            dict: Dictionary mapping show IDs to their watchlist status
        """
        try:
            # Ensure all show_ids are strings
            show_ids_str = [str(show_id) for show_id in show_ids]
            response = requests.post(
                f"{WATCHLIST_BACKEND_URL}/watchlist/batch",
                json={"username": username, "showIds": show_ids_str},
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error checking batch watchlist status: {e}")
            return {
                show_id: {"in_watchlist": False, "watched": False}
                for show_id in show_ids
            }


# Initialize the service
watchlist_service = WatchlistService()

# Initialize the blueprint
watchlist_bp = Blueprint("watchlist", __name__)

# OLD VERSION - Route handlers with direct database access
"""
@watchlist_bp.route("/my_watchlist")
@login_required
def my_watchlist():
    try:
        username = session.get("username")
        movies_data = get_watchlist_movies(username)
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
def add_to_watchlist_handler():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(request.referrer or url_for("search.index"))

        username = session.get("username")
        success = add_to_watchlist(username, show_id)
        return redirect(request.referrer or url_for("search.index"))
    except Exception as e:
        print(f"Error adding to watchlist: {e}")
        return redirect(request.referrer or url_for("search.index"))

@watchlist_bp.route("/remove_from_watchlist", methods=["POST"])
@login_required
def remove_from_watchlist_handler():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")
        success = remove_from_watchlist(username, show_id)
        return redirect(url_for("watchlist.my_watchlist"))
    except Exception as e:
        print(f"Error removing from watchlist: {e}")
        return redirect(url_for("watchlist.my_watchlist"))

@watchlist_bp.route("/mark_watched", methods=["POST"])
@login_required
def mark_watched_handler():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")
        success = update_watched_status(username, show_id, True)
        return redirect(url_for("watchlist.my_watchlist"))
    except Exception as e:
        print(f"Error marking as watched: {e}")
        return redirect(url_for("watchlist.my_watchlist"))

@watchlist_bp.route("/mark_unwatched", methods=["POST"])
@login_required
def mark_unwatched_handler():
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")
        success = update_watched_status(username, show_id, False)
        return redirect(url_for("watchlist.my_watchlist"))
    except Exception as e:
        print(f"Error marking as unwatched: {e}")
        return redirect(url_for("watchlist.my_watchlist"))
"""


# NEW VERSION - Route handlers using the watchlist microservice
@watchlist_bp.route("/my_watchlist")
@login_required
def my_watchlist():
    """Display the user's watchlist.
    The backend provides complete movie data with watchlist status."""
    try:
        username = session.get("username")
        movies_data = watchlist_service.get_watchlist(username)
        print(f"Movies data: {movies_data}")
        return render_template(
            "my_watchlist.html", username=username, movies=movies_data
        )
    except Exception as e:
        logger.error(f"Error retrieving watchlist: {e}")
        return render_template(
            "my_watchlist.html",
            username=username,
            movies=[],
            error="Error retrieving watchlist",
        )


@watchlist_bp.route("/add_to_watchlist", methods=["POST"])
@login_required
def add_to_watchlist_handler():
    """Handle adding a movie to the watchlist."""
    try:
        show_id = request.form.get("showId")
        username = session.get("username")

        logger.info(
            f"Adding to watchlist: username={username}, showId={show_id}"
        )
        logger.info(f"WATCHLIST_BACKEND_URL={WATCHLIST_BACKEND_URL}")

        if not show_id or not username:
            logger.error("Missing showId or username")
            return redirect(request.referrer or url_for("search.index"))

        success = watchlist_service.add_to_watchlist(username, show_id)

        if success:
            logger.info("Successfully added to watchlist")
        else:
            logger.error("Failed to add to watchlist")

        return redirect(request.referrer or url_for("search.index"))
    except Exception as e:
        logger.error(f"Error in add_to_watchlist_handler: {e}", exc_info=True)
        return redirect(request.referrer or url_for("search.index"))


@watchlist_bp.route("/remove_from_watchlist", methods=["POST"])
@login_required
def remove_from_watchlist_handler():
    """Handle removing a movie from the watchlist.
    The backend handles all validation and business logic."""
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")
        success = watchlist_service.remove_from_watchlist(username, show_id)
        return redirect(url_for("watchlist.my_watchlist"))
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        return redirect(url_for("watchlist.my_watchlist"))


@watchlist_bp.route("/mark_watched", methods=["POST"])
@login_required
def mark_watched_handler():
    """Handle marking a movie as watched.
    The backend handles all validation and status updates."""
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")
        success = watchlist_service.update_watched_status(
            username, show_id, True
        )
        return redirect(url_for("watchlist.my_watchlist"))
    except Exception as e:
        logger.error(f"Error marking as watched: {e}")
        return redirect(url_for("watchlist.my_watchlist"))


@watchlist_bp.route("/mark_unwatched", methods=["POST"])
@login_required
def mark_unwatched_handler():
    """Handle marking a movie as unwatched.
    The backend handles all validation and status updates."""
    try:
        show_id = request.form.get("showId")
        if not show_id:
            return redirect(url_for("watchlist.my_watchlist"))

        username = session.get("username")
        success = watchlist_service.update_watched_status(
            username, show_id, False
        )
        return redirect(url_for("watchlist.my_watchlist"))
    except Exception as e:
        logger.error(f"Error marking as unwatched: {e}")
        return redirect(url_for("watchlist.my_watchlist"))
