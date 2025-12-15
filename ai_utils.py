import os
import requests
import json
import re

# ==================== ENV ====================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

GROQ_API_KEY = GROQ_API_KEY.strip()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

# Use most stable Groq model
USER_MODEL = "llama3-70b-8192"
ADMIN_MODEL = "llama3-70b-8192"

# ==================== QUERY DETECTION ====================

QUERY_KEYWORDS = [
    "how", "what", "when", "where", "why", "can i", "could you",
    "help", "support", "question", "explain", "guide",
    "tell me", "show me", "does", "do you", "should i"
]

def is_query(text: str) -> bool:
    text = text.lower()
    if "?" in text:
        return True
    return sum(k in text for k in QUERY_KEYWORDS) >= 2

# ==================== CORE GROQ CALL ====================

def call_llm(prompt, model, max_tokens=120, temperature=0.4):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }

    try:
        r = requests.post(
            GROQ_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("❌ GROQ ERROR:", e)
        try:
            print("❌ GROQ RESPONSE:", r.text)
        except Exception:
            pass
        return ""

# ==================== USER RESPONSE (USED IN UI) ====================

def generate_user_reply(review: str, rating=None) -> str:
    if is_query(review):
        prompt = f"""
You are a polite customer support assistant.
Answer clearly in 2–3 short sentences (max 50 words).

Customer question:
"{review}"
"""
        response = call_llm(prompt, USER_MODEL, max_tokens=120, temperature=0.6)
    else:
        prompt = f"""
You are a customer support assistant.
Reply in ONE sentence (max 15 words).

If positive → thank warmly.
If negative → apologize sincerely.

Customer feedback:
"{review}"
"""
        response = call_llm(prompt, USER_MODEL, max_tokens=40, temperature=0.4)

    if not response:
        return (
            "Thank you for reaching out. Our team will assist you shortly."
            if is_query(review)
            else "Thank you for your feedback. We appreciate it."
        )

    return response

# ==================== ADMIN INSIGHTS (USED IN UI) ====================

def generate_admin_insights(review: str, rating=None):
    prompt = f"""
Analyze the feedback and return ONLY valid JSON:

{{
  "category": "positive | negative | query",
  "summary": "short summary",
  "recommended_action": "action to take"
}}

Feedback:
"{review}"
"""

    raw = call_llm(prompt, ADMIN_MODEL, max_tokens=180, temperature=0.3)

    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return "query", fallback_summary(review), fallback_action()

    try:
        parsed = json.loads(match.group())
        return (
            parsed.get("category", "query"),
            parsed.get("summary", fallback_summary(review)),
            parsed.get("recommended_action", fallback_action())
        )
    except Exception:
        return "query", fallback_summary(review), fallback_action()

# ==================== FALLBACKS ====================

def fallback_summary(review: str) -> str:
    return review[:80] + ("..." if len(review) > 80 else "")

def fallback_action() -> str:
    return "Review feedback and take appropriate action."
