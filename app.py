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
    "mongodb+srv://admin:LKt2lujE6czy468S@userauthcluster.obo8e.mongodb.net/user_authentication?retryWrites=true&w=majority&appName=UserAuthCluster",
)
mongo = PyMongo(app)
bcrypt = Bcrypt(app)


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
                return render_template(
                    "login.html", error="Invalid credentials"
                )

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

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            # Check if username already exists
            existing_user = mongo.db.users.find_one(
                {"username": request.form["username"]}
            )
            if existing_user:
                return "Username already exists", 400

            # Hash the password
            hashed_password = bcrypt.generate_password_hash(
                request.form["password"]
            ).decode("utf-8")

            # Create a new user
            user = {
                "username": request.form["username"],
                "password": hashed_password,
                "is_admin": False,  # Default to not admin
            }

            # Insert user into the database
            result = mongo.db.users.insert_one(user)

            if result.inserted_id:
                print("User successfully registered")
                return redirect(url_for("login"))
            else:
                return "Registration failed", 500

        except Exception as e:
            print(f"Registration error: {e}")
            return f"Registration failed: {str(e)}", 500

    return render_template("register.html")


@app.route("/search")
@login_required
def search():
    return render_template("search.html", username=session.get("username"))


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
