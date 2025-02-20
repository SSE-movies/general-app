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
from flask import Blueprint, render_template, jsonify, request, session
import bcrypt
from .database import supabase
from .decorators import admin_required

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


def get_user(user_id):
    """Fetch a user from the database by ID."""
    response = (
        supabase.table("profiles").select("*").eq("id", user_id).execute()
    )
    return response.data[0] if response.data else None


@admin_bp.route("/admin")
@admin_required
def dashboard():
    """Render the admin dashboard with user data."""
    try:
        users = supabase.table("profiles").select("*").execute().data
        return render_template(
            "admin.html", username=session.get("username"), users=users
        )
    except Exception as e:
        logger.error(f"Admin page error: {e}")
        return "Error loading admin page", 500


@admin_bp.route("/api/users")
@admin_required
def get_users():
    """Fetch all users from the database."""
    try:
        return jsonify(supabase.table("profiles").select("*").execute().data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/users/<user_id>/reset-password", methods=["POST"])
@admin_required
def reset_password(user_id):
    """Reset a user's password."""
    try:
        new_password = request.json.get("newPassword")
        if not new_password:
            return jsonify({"error": "New password is required"}), 400

        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        supabase.table("profiles").update({"password": hashed_password}).eq(
            "id", user_id
        ).execute()

        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/users/<user_id>/username", methods=["PUT"])
@admin_required
def update_username(user_id):
    """Update a user's username."""
    try:
        new_username = request.json.get("newUsername")
        if not new_username:
            return jsonify({"error": "New username is required"}), 400

        supabase.table("profiles").update({"username": new_username}).eq(
            "id", user_id
        ).execute()
        return jsonify({"message": "Username updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Delete a user from the database."""
    try:
        user_data = get_user(user_id)
        if not user_data:
            return jsonify({"error": "User not found"}), 404

        if user_data.get("is_admin"):
            return jsonify({"error": "Cannot delete admin user"}), 403

        supabase.table("watchlist").delete().eq(
            "username", user_data["username"]
        ).execute()
        supabase.table("profiles").delete().eq("id", user_id).execute()

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({"error": str(e)}), 500
