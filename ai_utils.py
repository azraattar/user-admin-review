import requests
import json
import re
import random

OLLAMA_URL = "http://localhost:11434/api/generate"

# Fast model for classification + short replies
USER_MODEL = "phi3"

# Better model for admin insights
ADMIN_MODEL = "phi3"

# ---------- RESPONSE TEMPLATES ----------
POSITIVE_RESPONSES = [
    "Thank you so much for your kind feedback! We really appreciate it.",
    "We're glad you had a great experience. Thanks for sharing!",
    "Your positive feedback means a lot to us. Thank you!"
]

NEGATIVE_RESPONSES = [
    "We're very sorry for the inconvenience caused. Please accept our apologies.",
    "Thank you for letting us know — we sincerely regret this experience.",
    "We apologize for this issue and appreciate your patience."
]

# ---------- AI CATEGORY CLASSIFIER ----------
def classify_feedback_ai(review, rating):
    prompt = f"""
Classify the following feedback into ONE word only:
POSITIVE, NEGATIVE, or QUERY.

Rating: {rating}
Feedback: "{review}"
"""

    payload = {
        "model": USER_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 3
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json().get("response", "").strip().upper()

        if "POSITIVE" in result:
            return "positive"
        if "NEGATIVE" in result:
            return "negative"
        return "query"

    except Exception:
        # Fallback to rating-based logic
        if rating >= 4:
            return "positive"
        elif rating <= 2:
            return "negative"
        else:
            return "query"

# ---------- AI RESPONSE FOR QUERY ----------
def generate_query_response_ai(review):
    prompt = f"""
Reply to the following user feedback in TWO short sentence.
Use a helpful and supportive tone.

Feedback: "{review}"
"""

    payload = {
        "model": USER_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 45
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=20)
        response.raise_for_status()
        return response.json().get("response", "").strip()

    except Exception:
        return "Thank you for reaching out. Our team will look into this."

# ---------- FINAL USER RESPONSE ----------
def generate_user_reply(review, rating):
    category = classify_feedback_ai(review, rating)

    if category == "positive":
        return random.choice(POSITIVE_RESPONSES)

    if category == "negative":
        return random.choice(NEGATIVE_RESPONSES)

    # QUERY → AI response
    return generate_query_response_ai(review)

# ---------- ADMIN INSIGHTS ----------
def generate_admin_insights(review, rating):
    prompt = f"""
You are an AI analyst.

Return valid JSON ONLY with:
- summary (one sentence)
- recommended_action (short business action)

Rating: {rating}
Review: "{review}"
"""

    payload = {
        "model": ADMIN_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 160
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()

        raw_text = response.json().get("response", "")
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)

        if not match:
            raise ValueError("No JSON found")

        parsed = json.loads(match.group())
        return (
            parsed.get("summary", "Summary unavailable."),
            parsed.get("recommended_action", "No action suggested.")
        )

    except Exception:
        return "Summary unavailable.", "No action suggested."
