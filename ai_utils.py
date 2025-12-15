import os
import requests
import json
import re
import random

# -------------------- OPENROUTER CONFIG --------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://ai-feedback-system",
    "X-Title": "AI Feedback System"
}

USER_MODEL = "mistralai/mistral-7b-instruct:free"
ADMIN_MODEL = "mistralai/mistral-7b-instruct:free"

# -------------------- QUERY DETECTION --------------------
QUERY_KEYWORDS = [
    "how", "what", "when", "where", "why", "can you", "could you",
    "help", "support", "question", "clarify", "explain"
]

def is_query(review):
    text = review.lower()
    score = sum(1 for kw in QUERY_KEYWORDS if kw in text)
    return "?" in text or score >= 1

# -------------------- CORE LLM CALL --------------------
def call_llm(prompt, model, max_tokens=60, temperature=0.4):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=HEADERS,
            json=payload,
            timeout=25
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

# -------------------- USER RESPONSE --------------------
def generate_user_reply(review, rating):
    query = is_query(review)

    if query:
        prompt = f"""
You are a helpful customer support assistant.
Answer the user's question clearly in 1–2 short sentences.

Question: "{review}"
"""
        response = call_llm(prompt, USER_MODEL, max_tokens=80, temperature=0.6)

    else:
        prompt = f"""
Respond to this feedback in ONE short sentence.

If positive → express appreciation  
If negative → apologize politely

Feedback: "{review}"
"""
        response = call_llm(prompt, USER_MODEL, max_tokens=40, temperature=0.5)

    # ✅ Only fallback if AI truly failed
    if response is None or response.strip() == "":
        if query:
            return "Thank you for your question. Our team will assist you shortly."
        return "Thank you for your feedback. We appreciate you taking the time to share it."

    return response

# -------------------- ADMIN INSIGHTS --------------------
def generate_admin_insights(review, rating):
    prompt = f"""
Return ONLY valid JSON.

Format:
{{
  "summary": "one sentence summary",
  "recommended_action": "short business action"
}}

Feedback: "{review}"
"""

    raw = call_llm(prompt, ADMIN_MODEL, max_tokens=180, temperature=0.3)

    if not raw:
        return fallback_summary(review), fallback_action()

    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return fallback_summary(review), fallback_action()

    try:
        parsed = json.loads(match.group())
        return (
            parsed.get("summary", fallback_summary(review)),
            parsed.get("recommended_action", fallback_action())
        )
    except Exception:
        return fallback_summary(review), fallback_action()

# -------------------- FALLBACKS --------------------
def fallback_summary(review):
    return review[:80] + ("..." if len(review) > 80 else "")

def fallback_action():
    return "Review feedback and take appropriate action."
