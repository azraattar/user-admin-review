import os
import requests
import json
import re

# ==================== ENV (SAFE & DEPLOYMENT READY) ====================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. "
        "Please set it in the environment variables."
    )

OPENROUTER_API_KEY = OPENROUTER_API_KEY.strip()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

# ✅ STABLE MODELS FOR DEPLOYMENT
USER_MODEL = "google/gemma-7b-it"
ADMIN_MODEL = "google/gemma-7b-it"

# ==================== QUERY DETECTION ====================

QUERY_KEYWORDS = [
    "how", "what", "when", "where", "why", "can i", "could you",
    "please help", "help", "support", "question", "wondering",
    "clarify", "explain", "guide", "tell me", "show me", "?",
    "does this", "do you", "is there", "will this", "should i"
]

def is_query(review):
    review_lower = review.lower()
    if "?" in review_lower:
        return True
    return sum(kw in review_lower for kw in QUERY_KEYWORDS) >= 2

# ==================== CORE LLM CALL ====================

def call_llm(prompt, model, max_tokens=50, temperature=0.2):
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
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        # 🔍 Safe debug for Render / Streamlit logs
        print("[AI ERROR]", str(e))
        return ""

# ==================== USER RESPONSE ====================

def generate_user_reply(review, rating):
    is_question = is_query(review)

    if is_question:
        prompt = f"""You are a helpful customer service assistant.
Answer clearly in 2–3 sentences (max 50 words).

Question: "{review}"
"""
        response = call_llm(prompt, USER_MODEL, max_tokens=100, temperature=0.6)

    else:
        prompt = f"""You are a customer service assistant.
Reply in ONE sentence (max 15 words).

If positive → thank warmly
If negative → apologize sincerely

Feedback: "{review}"
"""
        response = call_llm(prompt, USER_MODEL, max_tokens=40, temperature=0.5)

    if not response or len(response) < 5:
        if is_question:
            return "Thank you for reaching out! Our support team will assist you shortly."
        return "Thank you for your feedback. We appreciate you reaching out!"

    return response

# ==================== ADMIN INSIGHTS ====================

def generate_admin_insights(review, rating):
    prompt = f"""Analyze this feedback and return ONLY valid JSON:

{{"category":"positive/negative/query",
  "summary":"brief summary",
  "recommended_action":"action"}}

Feedback: "{review}"
"""

    raw = call_llm(prompt, ADMIN_MODEL, max_tokens=150, temperature=0.3)

    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return "query", fallback_summary(review), fallback_action_generic()

    try:
        parsed = json.loads(match.group())
        return (
            parsed.get("category", "query"),
            parsed.get("summary", fallback_summary(review)),
            parsed.get("recommended_action", fallback_action_generic())
        )
    except Exception:
        return "query", fallback_summary(review), fallback_action_generic()

# ==================== FALLBACKS ====================

def fallback_summary(review):
    return review[:80] + ("..." if len(review) > 80 else "")

def fallback_action_generic():
    return "Review feedback and take appropriate action."
