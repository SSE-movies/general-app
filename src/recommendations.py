"""Blueprint for handling movie recommendations using the Gemini API."""
import json
import os

from dotenv import load_dotenv
from flask import Blueprint, render_template
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/recommendations")

# Initialise the Gemini API by configuring the API key.
genai.configure(api_key=GEMINI_API_KEY)

@recommendations_bp.route("", methods=["GET"])
def recommendations():
    prompt = (
        "Provide a JSON array of 5 movie recommendations. "
        "Each recommendation should include the following fields: "
        "title, description, posterUrl, and showId. "
        "Return only the JSON array without any additional text."
    )
    try:
        # Instantiate the Gemini model (using "gemini-2.0-flash" as the model identifier)
        model = genai.GenerativeModel("gemini-2.0-flash") # noqa: E1101
        response = model.generate_content(prompt)
        recommendations_list = json.loads(response.text)
    except Exception as e:
        recommendations_list = []
        print("Error generating recommendations:", e)

    return render_template(
        "recommendations.html", recommendations=recommendations_list
        )
