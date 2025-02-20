"""
Authentication decorators for login and admin access control.
"""

import logging
from functools import wraps
from flask import session, redirect, url_for, flash, current_app

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
        testing = current_app.config.get('TESTING', False)
        if "username" not in session:
            if testing:
                return redirect(url_for("auth.login"), code=302)
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):
    """
    Decorator to restrict access to admin users.
    Redirects to login page if user is not an admin.
    """

    @wraps(f)
    @login_required  # Ensure user is logged in before checking admin status
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            logger.warning(
                f"Unauthorized admin access attempt by user: {session.get('username')}"
            )
            return redirect(url_for("auth.login"))  # Redirect to login page

        return f(*args, **kwargs)

    return decorated_function
