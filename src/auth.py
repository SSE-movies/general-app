"""
Authentication Blueprint for user login, registration, and logout.

Routes:
- `/login` (GET, POST): User authentication
- `/register` (GET, POST): User registration
- `/logout` (GET): User logout
"""

import logging
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)
import bcrypt
from .database import supabase

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


def get_user_by_username(username):
    """Fetch user data by username."""
    response = (
        supabase.table("profiles")
        .select("*")
        .eq("username", username)
        .execute()
    )
    return response.data[0] if response.data else None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    success = request.args.get("success")

    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            user_data = get_user_by_username(username)
            if not user_data:
                return render_template(
                    "login.html",
                    show_navbar=False,
                    error="Invalid credentials",
                )

            if bcrypt.checkpw(
                password.encode("utf-8"), user_data["password"].encode("utf-8")
            ):
                session.clear()
                session["user_id"] = user_data["id"]
                session["username"] = user_data["username"]
                session["is_admin"] = user_data["is_admin"]

                return redirect(
                    url_for(
                        "admin.dashboard"
                        if user_data["is_admin"]
                        else "search.index"
                    )
                )

            return render_template(
                "login.html", show_navbar=False, error="Invalid credentials"
            )

        except KeyError as e:
            logger.error(f"Missing form field: {e}")
            return render_template(
                "login.html",
                show_navbar=False,
                error="Missing username or password.",
            )
        except Exception as e:
            logger.error(f"Unexpected login error: {e}")
            return render_template(
                "login.html",
                show_navbar=False,
                error="An error occurred. Please try again.",
            )

    return render_template("login.html", show_navbar=False, success=success)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
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

            if get_user_by_username(username):
                return render_template(
                    "register.html",
                    show_navbar=False,
                    error="Username already exists",
                )

            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            profile_data = {
                "username": username,
                "password": hashed_password,
                "is_admin": False,
            }

            supabase.table("profiles").insert(profile_data).execute()

            return redirect(
                url_for(
                    "auth.login",
                    success="Registration successful. Please login now.",
                )
            )

        except KeyError as e:
            logger.error(f"Missing form field: {e}")
            return render_template(
                "register.html",
                show_navbar=False,
                error="Missing username or password.",
            )
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return render_template(
                "register.html",
                show_navbar=False,
                error="An error occurred. Please try again.",
            )

    return render_template("register.html", show_navbar=False)


@auth_bp.route("/logout")
def logout():
    """Log out the user and clear session."""
    session.clear()
    return redirect(url_for("auth.login"))  # Redirect to login page
