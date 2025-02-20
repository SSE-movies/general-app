from flask import Blueprint, render_template, jsonify, request, session
import bcrypt
from .database import supabase
from .decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin")
@admin_required
def dashboard():
    try:
        response = supabase.table("profiles").select("*").execute()
        users = response.data
        return render_template(
            "admin.html",
            username=session.get("username"),
            users=users
        )
    except Exception as e:
        print(f"Admin page error: {e}")
        return "Error loading admin page", 500

@admin_bp.route("/api/users")
@admin_required
def get_users():
    try:
        response = supabase.table("profiles").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/users/<user_id>/reset-password", methods=["POST"])
@admin_required
def reset_password(user_id):
    try:
        new_password = request.json.get("newPassword")
        if not new_password:
            return jsonify({"error": "New password is required"}), 400

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), salt)

        supabase.table("profiles").update(
            {"password": hashed_password.decode("utf-8")}
        ).eq("id", user_id).execute()

        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/users/<user_id>/username", methods=["PUT"])
@admin_required
def update_username(user_id):
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
    try:
        user_data = supabase.table("profiles").select("*").eq("id", user_id).execute().data

        if not user_data:
            return jsonify({"error": "User not found"}), 404

        if user_data[0].get("is_admin"):
            return jsonify({"error": "Cannot delete admin user"}), 403

        supabase.table("watchlist").delete().eq("username", user_data[0]["username"]).execute()

        supabase.table("profiles").delete().eq("id", user_id).execute()

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting user: {e}")
        return jsonify({"error": str(e)}), 500