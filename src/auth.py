from flask import Blueprint, render_template, request, redirect, url_for, session
import bcrypt
from .database import supabase

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    success = request.args.get("success")
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

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

            if bcrypt.checkpw(
                    password.encode("utf-8"), user_data["password"].encode("utf-8")
            ):
                session["user_id"] = user_data["id"]
                session["username"] = user_data["username"]
                session["is_admin"] = user_data["is_admin"]

                if user_data["is_admin"]:
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("search.index"))
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

            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

            profile_data = {
                "username": username,
                "password": hashed_password.decode("utf-8"),
                "is_admin": False,
            }

            supabase.table("profiles").insert(profile_data).execute()

            return redirect(
                url_for(
                    "auth.login",
                    success="Registration successful. Please login now.",
                )
            )

        except Exception as e:
            print(f"Registration error: {e}")
            return render_template(
                "register.html", show_navbar=False, error=str(e)
            )

    return render_template("register.html", show_navbar=False)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))