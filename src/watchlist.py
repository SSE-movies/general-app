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
from .database import get_movie_details_by_id

# Set up logging
logger = logging.getLogger(__name__)

# Constants
TIMEOUT_SECONDS = 10

# Get configuration from environment
WATCHLIST_BACKEND_URL = os.environ.get("WATCHLIST_BACKEND_URL")


class WatchlistService:
    """Service class for interacting with the watchlist backend API.
    This is a thin client that delegates most logic to the backend service."""

    @staticmethod
    def get_watchlist(username):
        """Get all movies in a user's watchlist with full movie details."""
        try:
            response = requests.get(
                f"{WATCHLIST_BACKEND_URL}/watchlist/{username}",
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()

            if "entries" not in data:
                logger.error(
                    "Unexpected response structure", extra={"data": data}
                )
                return []

            return data["entries"]
        except Exception as e:
            logger.error(
                "Error fetching watchlist",
                extra={"error": str(e), "username": username},
            )
            return []

    @staticmethod
    def add_to_watchlist(username, show_id):
        """Add a movie to the user's watchlist."""
        try:
            show_id_str = str(show_id)
            logger.info(
                "Adding movie to watchlist",
                extra={
                    "username": username,
                    "show_id": show_id_str,
                    "watchlist_url": WATCHLIST_BACKEND_URL,
                },
            )

            response = requests.post(
                f"{WATCHLIST_BACKEND_URL}/watchlist",
                json={"username": username, "showId": show_id_str},
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return True
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


@watchlist_bp.route("/my_watchlist")
@login_required
def my_watchlist():
    """Display the user's watchlist.
    The backend provides complete movie data with watchlist status."""
    try:
        username = session.get("username")

        # Retrieve the watchlist entries (each with showId and watched status)
        watchlist_entries = watchlist_service.get_watchlist(username)
        full_movies = []

        for entry in watchlist_entries:
            show_id = entry.get("showId")
            # Fetch movie details using movie API
            movie_details = get_movie_details_by_id(str(show_id))

            if movie_details:
                # Merge the watched status into the movie details
                movie_details["watched"] = entry.get("watched", False)
                full_movies.append(movie_details)

            else:
                logger.error(f"Movie details not found for showId: {show_id}")

        logger.info(f"Full movies data: {full_movies}")

        return render_template(
            "my_watchlist.html", username=username, movies=full_movies
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

        if success:
            logger.info("Successfully removed from watchlist")
        else:
            logger.error("Failed remove from watchlist")

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
