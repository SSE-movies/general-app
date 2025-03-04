"""Blueprint for handling movie recommendations using the Gemini API."""

import json
from flask import Blueprint, render_template
from google import genai

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')

# Initialize the Gemini API client using Zev's key
client = genai.Client(api_key="AIzaSyB7HbAnWnVgVBfG_Ah727BOVudbhBH8Ras")

@recommendations_bp.route("", methods=["GET"])
def recommendations():
    # Construct a prompt for the Gemini API to return movie recommendations as JSON.
    prompt = (
        "Provide a JSON array of 5 movie recommendations. "
        "Each recommendation should include the following fields: "
        "title, description, posterUrl, and showId. "
        "Return only the JSON array without any additional text."
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        # Parse the JSON output from the API
        recommendations_list = json.loads(response.text)
    except Exception as e:
        recommendations_list = []
        print("Error generating recommendations:", e)
    
    return render_template("recommendations.html", recommendations=recommendations_list)
