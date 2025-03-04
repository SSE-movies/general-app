"""Watchlist blueprint for managing user movie watchlists."""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)
from .database import (
    get_watchlist_movies,
    add_to_watchlist,
    remove_from_watchlist,
    update_watched_status,
)
from .decorators import login_required

watchlist_bp = Blueprint("watchlist", __name__)


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
