"""Blueprint for handling movie recommendations using the Generative AI API."""

import json
import os

from dotenv import load_dotenv
from flask import Blueprint, render_template
from google import genai
from google.genai import types

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

recommendations_bp = Blueprint(
    "recommendations", __name__, url_prefix="/recommendations"
)

# Create the client with your API key.
client = genai.Client(api_key=GEMINI_API_KEY)


def strip_markdown(text):
    """Strip markdown formatting if the response is wrapped in triple backticks."""
    if text.startswith("```json"):
        text = text[len("```json") :].strip()
    elif text.startswith("```"):
        text = text[len("```") :].strip()
    if text.endswith("```"):
        text = text[: -len("```")].strip()
    return text


@recommendations_bp.route("", methods=["GET"])
def recommendations():
    """Generate a JSON array of 3 movie recommendations using a Generative AI model."""
    prompt = (
        "Provide a JSON array of 3 movie recommendations. "
        "Each recommendation should include the following fields: "
        "title, description, and releaseYear. "
        "Return only the JSON array without any additional text or markdown formatting. "
        "Ensure the response is valid JSON."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Change the model if needed.
            contents=[prompt],
            config=types.GenerateContentConfig(
                max_output_tokens=500,  # Adjust as necessary for your response length.
                temperature=0.7,
            ),
        )
        raw_text = response.text.strip()
        raw_text = strip_markdown(raw_text)

        if not raw_text:
            raise ValueError("Empty response from the Generative AI model.")

        recommendations_list = json.loads(raw_text)
    except Exception as e:
        recommendations_list = []
        print("Error generating recommendations:", e)

    return render_template(
        "recommendations.html", recommendations=recommendations_list
    )
