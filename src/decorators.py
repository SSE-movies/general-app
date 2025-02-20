"""
Authentication decorators for login and admin access control.
"""

import logging
from functools import wraps
from flask import session, redirect, url_for, flash

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def login_required(f):
    """
    Decorator to restrict access to authenticated users.
    Redirects to login page if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):
    """
    Decorator to restrict access to admin users.
    Redirects to home page if user is not an admin.
    """
    @wraps(f)
    @login_required  # Ensure user is logged in before checking admin status
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            logger.warning(f"Unauthorized admin access attempt by user: {session.get('username')}")
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("index"))  # Redirect to homepage instead of login

        return f(*args, **kwargs)

    return decorated_function
