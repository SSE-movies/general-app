"""Authentication blueprint for user login, registration, and logout."""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
)
import bcrypt
from .database import supabase
from .decorators import login_required
import re

auth_bp = Blueprint("auth", __name__)

def is_valid_password(password):
    """Check if password meets security requirements."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
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
                    error="Invalid credentials"
                )

            user_data = user_response.data[0]

            # Verify password
            if bcrypt.checkpw(
                password.encode("utf-8"),
                user_data["password"].encode("utf-8")
            ):
                # Store user info in session
                session["user_id"] = user_data["id"]
                session["username"] = user_data["username"]
                session["is_admin"] = user_data.get("is_admin", False)

                # Redirect based on user type
                if user_data.get("is_admin"):
                    return redirect(url_for("admin.dashboard"))

                # Redirect to the same search endpoint that's working in the navbar
                return redirect(url_for("search.index"))
            else:
                return render_template(
                    "login.html",
                    show_navbar=False,
                    error="Invalid credentials"
                )

        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            return render_template(
                "login.html",
                show_navbar=False,
                error="Invalid credentials"
            )

    return render_template("login.html", show_navbar=False, success=success)

@auth_bp.route("/logout")
def logout():
    """Log out the user by clearing session data."""
    session.clear()  # Remove user data from session
    return redirect(url_for("auth.login"))  # Redirect to login page

@auth_bp.route("/register", methods=["GET", "POST"])
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

            # Validate password
            password_error = is_valid_password(password)
            if password_error:
                return render_template(
                    "register.html",
                    show_navbar=False,
                    error=password_error,
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
                    "auth.login",
                    success="Registration successful. Please login now."
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
