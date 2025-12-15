import os
import requests
import json
import re

# ==================== ENV ====================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in environment variables")

GROQ_API_KEY = GROQ_API_KEY.strip()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

# Fast + reliable models
USER_MODEL = "llama3-8b-8192"
ADMIN_MODEL = "llama3-8b-8192"

# ==================== QUERY DETECTION ====================

QUERY_KEYWORDS = [
    "how", "what", "when", "where", "why", "can i", "could you",
    "please help", "help", "support", "question", "wondering",
    "clarify", "explain", "guide", "tell me", "show me", "?",
    "does this", "do you", "is there", "will this", "should i"
]

def is_query(review):
    text = review.lower()
    if "?" in text:
        return True
    return sum(k in text for k in QUERY_KEYWORDS) >= 2

# ==================== CORE LLM CALL ====================

def call_llm(prompt, model, max_tokens=80, temperature=0.3):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        r = requests.post(GROQ_URL, headers=HEADERS, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("[LLM ERROR]", e)
        return ""

# ==================== USER RESPONSE ====================

def generate_user_reply(review, rating):
    is_question = is_query(review)

    if is_question:
        prompt = f"""
You are a helpful customer service assistant.
Answer clearly in 2–3 sentences (max 50 words).

Question: "{review}"
"""
        response = call_llm(prompt, USER_MODEL, max_tokens=120, temperature=0.6)
    else:
        prompt = f"""
You are a customer service assistant.
Reply in ONE sentence (max 15 words).

If positive → thank warmly
If negative → apologize sincerely

Feedback: "{review}"
"""
        response = call_llm(prompt, USER_MODEL, max_tokens=40, temperature=0.4)

    if not response:
        return (
            "Thank you for reaching out! Our team will assist you shortly."
            if is_question
            else "Thank you for your feedback. We appreciate it."
        )

    return response

# ==================== ADMIN INSIGHTS ====================

def generate_admin_insights(review, rating):
    prompt = f"""
Analyze this feedback and return ONLY valid JSON:

{{
  "category": "positive/negative/query",
  "summary": "brief summary",
  "recommended_action": "action"
}}

Feedback: "{review}"
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

def fallback_summary(review):
    return review[:80] + ("..." if len(review) > 80 else "")

def fallback_action():
    return "Review feedback and take appropriate action."
