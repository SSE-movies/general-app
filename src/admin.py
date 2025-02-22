"""
Admin Blueprint for managing users.

This module provides routes for:
- Viewing the admin dashboard
- Fetching user data
- Resetting user passwords
- Updating usernames
- Deleting users
"""

import logging
from flask import Blueprint, render_template, jsonify, request, session, flash
import bcrypt
from .database import supabase
from .decorators import admin_required

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Fix the Blueprint creation syntax
admin_bp = Blueprint("admin", __name__)

def get_user(user_id):
    """
    Fetch a user from the database by ID.

    Args:
        user_id: The ID of the user to fetch

    Returns:
        dict: User data if found, None otherwise
    """
    try:
        response = (
            supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return None

def validate_new_username(username):
    """
    Validate a new username.

    Args:
        username: The username to validate

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters long"

    # Check if username already exists
    try:
        existing = supabase.table("profiles").select("*").eq("username", username).execute()
        if existing.data:
            return False, "Username already exists"
    except Exception as e:
        logger.error(f"Error checking username existence: {e}")
        return False, "Error validating username"

    return True, None

@admin_bp.route("/admin")
@admin_required
def dashboard():
    """Render the admin dashboard with user data."""
    try:
        users = supabase.table("profiles").select("*").execute().data
        return render_template(
            "admin.html",
            username=session.get("username"),
            users=users,
            is_admin=session.get("is_admin", False)
        )
    except Exception as e:
        logger.error(f"Admin page error: {e}")
        flash("Error loading admin dashboard", "error")
        return render_template("admin.html", error="Failed to load user data"), 500

@admin_bp.route("/api/users")
@admin_required
def get_users():
    """Fetch all users from the database."""
    try:
        users = supabase.table("profiles").select("*").execute().data
        # Remove sensitive information
        for user in users:
            user.pop("password", None)
        return jsonify(users)
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500

@admin_bp.route("/api/users/<user_id>/reset-password", methods=["POST"])
@admin_required
def reset_password(user_id):
    """Reset a user's password."""
    try:
        new_password = request.json.get("newPassword")
        if not new_password or len(new_password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400

        # Check if user exists
        user = get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Hash and update password
        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        supabase.table("profiles").update(
            {"password": hashed_password}
        ).eq("id", user_id).execute()

        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return jsonify({"error": "Failed to reset password"}), 500

@admin_bp.route("/api/users/<user_id>/username", methods=["PUT"])
@admin_required
def update_username(user_id):
    """Update a user's username."""
    try:
        new_username = request.json.get("newUsername", "").strip()

        # Validate new username
        is_valid, error_message = validate_new_username(new_username)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        # Check if user exists
        user = get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update username in profiles
        supabase.table("profiles").update(
            {"username": new_username}
        ).eq("id", user_id).execute()

        # Update username in watchlist
        supabase.table("watchlist").update(
            {"username": new_username}
        ).eq("username", user["username"]).execute()

        return jsonify({"message": "Username updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating username: {e}")
        return jsonify({"error": "Failed to update username"}), 500

@admin_bp.route("/api/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Delete a user from the database, preventing self-deletion."""
    try:
        # Get the current logged-in user's details
        current_username = session.get("username")

        # Check if the user to be deleted exists
        user = get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Prevent the logged-in admin from deleting themselves
        if user["username"] == current_username:
            return jsonify({"error": "You cannot delete yourself!"}), 403

        # Prevent deletion of other admin users
        if user.get("is_admin"):
            return jsonify({"error": "Cannot delete another admin user"}), 403

        # Delete user's watchlist entries first
        supabase.table("watchlist").delete().eq(
            "username", user["username"]
        ).execute()

        # Then delete the user
        supabase.table("profiles").delete().eq("id", user_id).execute()

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({"error": "Failed to delete user"}), 500
