"""Flask application factory module."""
import os
from dotenv import load_dotenv
from flask import Flask, render_template

# Load environment variables
load_dotenv()

def create_app(testing=False):  # Add 'testing' parameter
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv('FLASK_SECRET_KEY')

    # Set testing configurations if testing mode is enabled
    if testing:
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF in tests

    # Import blueprints
    from .auth import auth_bp
    from .search import search_bp
    from .watchlist import watchlist_bp
    from .admin import admin_bp

    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp)
    app.register_blueprint(search_bp, url_prefix="/")
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        """Render the index page."""
        return render_template("index.html", show_navbar=False)

    return app
