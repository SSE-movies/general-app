"""Blueprint for handling movie recommendations using the Google Generative AI API."""
import json
import os

from dotenv import load_dotenv
from flask import Blueprint, render_template
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/recommendations")

# Configure the Google Generative AI client with your API key.
genai.configure(api_key=GEMINI_API_KEY)

@recommendations_bp.route("", methods=["GET"])
def recommendations():
    """
    Generate a JSON array of 5 movie recommendations using a Generative AI model.
    Each recommendation should have title, description, posterUrl, and showId.
    """
    prompt = (
        "Provide a JSON array of 5 movie recommendations. "
        "Each recommendation should include the following fields: "
        "title, description, posterUrl, and showId. "
        "Return only the JSON array without any additional text."
    )

    try:
        # Use the new generate_text function (or generate_chat) with a valid model name.
        # For example, "models/text-bison-001".
        response = genai.generate_text(
            model="models/text-bison-001",  # Or another valid model
            prompt=prompt,
            temperature=0.7,
        )
        # The returned text is in response.generations[0].text
        raw_text = response.generations[0].text
        recommendations_list = json.loads(raw_text)
    except Exception as e:
        recommendations_list = []
        print("Error generating recommendations:", e)

    return render_template(
        "recommendations.html", recommendations=recommendations_list
        )
