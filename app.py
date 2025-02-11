from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from functools import wraps
import os
from bson.objectid import ObjectId

app = Flask(
    __name__, template_folder="src/templates", static_folder="src/static"
)

# Configuration
app.config["SECRET_KEY"] = os.urandom(24)
app.config["MONGO_URI"] = os.getenv(
    "MONGO_URI",
    "mongodb+srv://admin:admin@userauthcluster.obo8e.mongodb.net/user_authentication?retryWrites=true&w=majority&appName=UserAuthCluster",
)
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

try:
    # Test MongoDB connection
    mongo.db.command("ping")
    print("MongoDB connection successful!")
    print("Available collections:", mongo.db.list_collection_names())
except Exception as e:
    print(f"MongoDB Connection Error: {str(e)}")
    raise Exception(f"Failed to connect to MongoDB: {str(e)}")


# Database initialization
def init_db():
    try:
        # Check if the users collection exists
        if "users" not in mongo.db.list_collection_names():
            # Create the users collection
            mongo.db.create_collection("users")
            print("Users collection created successfully")

        # Check if there's at least one admin user
        admin_user = mongo.db.users.find_one({"is_admin": True})
        if not admin_user:
            # Create a default admin user if none exists
            default_admin = {
                "username": "admin",
                "password": bcrypt.generate_password_hash("admin123").decode(
                    "utf-8"
                ),
                "is_admin": True,
            }
            mongo.db.users.insert_one(default_admin)
            print("Default admin user created")

    except Exception as e:
        print(f"Database initialization error: {e}")


# Initialize database
init_db()


# Authentication decorators
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
        user = mongo.db.users.find_one(
            {"_id": ObjectId(session["user_id"])}
        )  # Convert string ID to ObjectId
        if not user or not user.get("is_admin"):
            return redirect(
                url_for("login")
            )  # Redirect instead of showing error
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    success = request.args.get(
        "success"
    )  # Get success message from URL if it exists
    if request.method == "POST":
        try:
            # Get user from MongoDB
            user = mongo.db.users.find_one(
                {"username": request.form["username"]}
            )

            if not user:
                return render_template("login.html", error="User not found")

            # Check password
            if not bcrypt.check_password_hash(
                user["password"], request.form["password"]
            ):
                return render_template("login.html", error="Invalid password")

            # If credentials are valid, set session and redirect
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            session["is_admin"] = user.get("is_admin", False)

            if user.get("is_admin"):
                return redirect(url_for("admin"))
            return redirect(url_for("search"))

        except Exception as e:
            print(f"Login error: {e}")
            return render_template(
                "login.html", error="Login failed. Please try again."
            )

    return render_template(
        "login.html", success=success
    )  # Pass success message to template


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            # Input validation
            if not username or not password:
                return render_template(
                    "register.html", error="Username and password are required"
                )

            # Check if username already exists
            try:
                existing_user = mongo.db.users.find_one({"username": username})
                if existing_user:
                    return render_template(
                        "register.html", error="Username already exists"
                    )
            except Exception as db_error:
                print(f"Database query error: {db_error}")
                return render_template(
                    "register.html",
                    error="Unable to check username. Please try again later.",
                )

            # Hash the password
            try:
                hashed_password = bcrypt.generate_password_hash(
                    password
                ).decode("utf-8")
            except Exception as hash_error:
                print(f"Password hashing error: {hash_error}")
                return render_template(
                    "register.html",
                    error="Error processing password. Please try again.",
                )

            # Create a new user
            user = {
                "username": username,
                "password": hashed_password,
                "is_admin": False,
            }

            # Insert user into the database
            try:
                result = mongo.db.users.insert_one(user)
                if result.inserted_id:
                    print(f"User {username} successfully registered")
                    return redirect(
                        url_for(
                            "login",
                            success="Registration successful. Please login now.",
                        )
                    )
            except Exception as insert_error:
                print(f"Database insertion error: {insert_error}")
                return render_template(
                    "register.html",
                    error="Registration failed. Please try again later.",
                )

        except Exception as e:
            print(f"Registration error: {e}")
            return render_template(
                "register.html",
                error="An error occurred during registration. Please try again.",
            )

    return render_template("register.html")


# @app.route("/search", methods=["GET", "POST"])
@app.route("/search")
@login_required
def search():
    cast_inp       = request.values.get("cast", "").strip()
    country_inp    = request.values.get("country", "").strip()
    date_inp       = request.values.get("date_added", "").strip()
    desc_inp       = request.values.get("description", "").strip()
    dir_inp        = request.values.get("director", "").strip()
    dur_inp        = request.values.get("duration", "").strip()
    list_inp       = request.values.get("listed_in", "").strip()
    rating_inp     = request.values.get("rating", "").strip()
    year_inp       = request.values.get("release_year", "").strip()
    show_id_inp    = request.values.get("show_id", "").strip()
    title_inp      = request.values.get("title", "").strip()
    type_inp       = request.values.get("type", "").strip()

    # filtered = movies_data

    if cast_inp:
        filtered = [m for m in filtered if cast_inp.lower() in (m.get("cast") or "").lower()]
    if country_inp:
        filtered = [m for m in filtered if country_inp.lower() in (m.get("country") or "").lower()]
    if date_inp:
        filtered = [m for m in filtered if date_inp.lower() in (m.get("date_added") or "").lower()]
    if desc_inp:
        filtered = [m for m in filtered if desc_inp.lower() in (m.get("description") or "").lower()]
    if dir_inp:
        filtered = [m for m in filtered if dir_inp.lower() in (m.get("director") or "").lower()]
    if dur_inp:
        filtered = [m for m in filtered if dur_inp.lower() in (m.get("duration") or "").lower()]
    if list_inp:
        filtered = [m for m in filtered if list_inp.lower() in (m.get("listed_in") or "").lower()]
    if rating_inp:
        filtered = [m for m in filtered if rating_inp.lower() in (m.get("rating") or "").lower()]
    if year_inp.isdigit():
        year_val = int(year_inp)
        filtered = [m for m in filtered if m.get("release_year") == year_val]
    if show_id_inp:
        filtered = [m for m in filtered if show_id_inp.lower() in (m.get("show_id") or "").lower()]
    if title_inp:
        filtered = [m for m in filtered if title_inp.lower() in (m.get("title") or "").lower()]
    if type_inp:
        filtered = [m for m in filtered if type_inp.lower() in (m.get("type") or "").lower()]

    return render_template("search.html", username=session.get("username"), movies=filtered)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin():
    try:
        # Fetch all users, excluding password
        users = list(mongo.db.users.find({}, {"password": 0}))

        # Convert ObjectId to string
        for user in users:
            user["_id"] = str(user["_id"])

        return render_template(
            "admin.html", username=session.get("username"), users=users
        )
    except Exception as e:
        print(f"Admin page error: {e}")
        return "Error loading admin page", 500


# API Routes for admin functionality
@app.route("/api/users")
@admin_required
def get_users():
    try:
        users = list(mongo.db.users.find({}, {"password": 0}))
        for user in users:
            user["_id"] = str(user["_id"])
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<user_id>/reset-password", methods=["POST"])
@admin_required
def reset_password(user_id):
    try:
        # Get new password from request
        new_password = request.json.get("newPassword")

        if not new_password:
            return jsonify({"error": "New password is required"}), 400

        # Hash the new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode(
            "utf-8"
        )

        # Update user's password
        result = mongo.db.users.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"password": hashed_password}}
        )

        if result.modified_count > 0:
            return jsonify({"message": "Password updated successfully"}), 200
        else:
            return (
                jsonify({"error": "User not found or password unchanged"}),
                404,
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<user_id>/username", methods=["PUT"])
@admin_required
def update_username(user_id):
    try:
        new_username = request.json.get("newUsername")
        if not new_username:
            return jsonify({"error": "New username is required"}), 400

        # Convert string ID to ObjectId
        result = mongo.db.users.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"username": new_username}}
        )

        if result.modified_count > 0:
            return jsonify({"message": "Username updated successfully"}), 200
        else:
            return (
                jsonify({"error": "User not found or username unchanged"}),
                404,
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    try:
        # Convert string ID to ObjectId
        result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count > 0:
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
