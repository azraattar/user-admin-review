import os
import sys
import requests
import json
import re
from dotenv import load_dotenv

# -------------------- LOAD & DEBUG ENV --------------------
print("\n" + "="*70)
print("🔍 ENVIRONMENT VARIABLE DEBUG")
print("="*70)

# Force reload .env file with override
load_dotenv(override=True)
print(f"✓ Attempted to load .env file with override")

# Alternative: Try loading from specific path
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"✓ Loaded .env from: {env_path}")

# Check API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

print(f"\n📋 API Key Status:")
print(f"  • Exists: {OPENROUTER_API_KEY is not None}")
print(f"  • Type: {type(OPENROUTER_API_KEY)}")
print(f"  • Length: {len(OPENROUTER_API_KEY) if OPENROUTER_API_KEY else 0} characters")

if OPENROUTER_API_KEY:
    # Clean the key immediately
    OPENROUTER_API_KEY = OPENROUTER_API_KEY.strip().strip('"').strip("'")
    
    print(f"  • Starts with: '{OPENROUTER_API_KEY[:20]}...'")
    print(f"  • Ends with: '...{OPENROUTER_API_KEY[-10:]}'")
    print(f"  • Has whitespace: {' ' in OPENROUTER_API_KEY}")
    print(f"  • Has newlines: {'\\n' in OPENROUTER_API_KEY}")
    print(f"  • Has quotes: {'"' in OPENROUTER_API_KEY or "'" in OPENROUTER_API_KEY}")
else:
    print(f"  ❌ API KEY NOT FOUND!")
    print(f"\n📁 Current working directory: {os.getcwd()}")
    print(f"📁 Script directory: {os.path.dirname(__file__)}")
    print(f"📄 Looking for .env in: {os.path.join(os.getcwd(), '.env')}")
    print(f"📂 .env file exists: {os.path.exists('.env')}")
    print(f"📂 .env in script dir: {os.path.exists(env_path)}")
    
    # List all environment variables starting with OPEN or ROUTER
    all_env = {k: v[:20] + '...' for k, v in os.environ.items() if 'OPEN' in k.upper() or 'ROUTER' in k.upper()}
    print(f"\n🔑 Related environment variables: {all_env}")
    
    print(f"\n⚠️  FALLBACK: Using hardcoded key for testing")
    # TEMPORARY FALLBACK - Replace with your actual key for testing
    OPENROUTER_API_KEY = "sk-or-v1-PASTE_YOUR_KEY_HERE"  # ← PUT YOUR KEY HERE

print("="*70 + "\n")

# -------------------- OPENROUTER CONFIG --------------------
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Ensure key is clean
if OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = OPENROUTER_API_KEY.strip().strip('"').strip("'")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://streamlit.app",
    "X-Title": "AI Feedback System"
}

USER_MODEL = "mistralai/mistral-7b-instruct:free"
ADMIN_MODEL = "mistralai/mistral-7b-instruct:free"

# -------------------- QUERY DETECTION --------------------
QUERY_KEYWORDS = [
    "how", "what", "when", "where", "why", "can i", "could you", 
    "please help", "help", "support", "question", "wondering", 
    "clarify", "explain", "guide", "tell me", "show me", "?",
    "does this", "do you", "is there", "will this", "should i"
]

def is_query(review):
    """Detect if feedback is a question/query"""
    review_lower = review.lower()
    
    # Check for question mark
    if "?" in review:
        return True
    
    # Check for query keywords
    query_count = sum(1 for kw in QUERY_KEYWORDS if kw in review_lower)
    
    # If 2+ query keywords, likely a question
    return query_count >= 2

# -------------------- TEST API CONNECTION --------------------
# def test_api_connection():
#     """Test if API key works"""
#     print("\n" + "="*70)
#     print("🔌 TESTING API CONNECTION")
#     print("="*70)
    
#     if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "sk-or-v1-PASTE_YOUR_KEY_HERE":
#         print("❌ Cannot test - API key not configured properly\n")
#         print("⚠️  Please set OPENROUTER_API_KEY in .env file or hardcode it temporarily")
#         print("="*70 + "\n")
#         return False
    
#     try:
#         test_payload = {
#             "model": USER_MODEL,
#             "messages": [{"role": "user", "content": "Hi"}],
#             "max_tokens": 5
#         }
        
#         print(f"📤 Sending test request to: {OPENROUTER_URL}")
#         print(f"🔑 Using key: {OPENROUTER_API_KEY[:15]}...{OPENROUTER_API_KEY[-5:]}")
#         print(f"🤖 Model: {USER_MODEL}")
        
#         response = requests.post(
#             OPENROUTER_URL,
#             headers=HEADERS,
#             json=test_payload,
#             timeout=10
#         )
        
#         print(f"\n📥 Response Status: {response.status_code}")
        
#         if response.status_code == 200:
#             print("✅ API CONNECTION SUCCESSFUL!")
#             result = response.json()
#             print(f"💬 Test response: {result['choices'][0]['message']['content']}")
#             print("="*70 + "\n")
#             return True
#         else:
#             print(f"❌ API ERROR: {response.status_code}")
#             print(f"📄 Error body: {response.text}")
            
#             if response.status_code == 401:
#                 print("\n💡 FIX: Your API key is invalid. Please:")
#                 print("   1. Go to https://openrouter.ai/keys")
#                 print("   2. Create a new API key")
#                 print("   3. Update your .env file")
#                 print("   4. Restart the app")
            
#             print("="*70 + "\n")
#             return False
            
#     except Exception as e:
#         print(f"❌ CONNECTION FAILED: {e}")
#         print(f"🔍 Exception type: {type(e).__name__}")
#         print("="*70 + "\n")
#         return False

# # Run test on import
# test_api_connection()

# -------------------- CORE LLM CALL --------------------
def call_llm(prompt, model, max_tokens=50, temperature=0.2):
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
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
        result = response.json()["choices"][0]["message"]["content"].strip()
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"[HTTP ERROR] {e}")
        return ""
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {type(e).__name__}: {e}")
        return ""

# ---------- SMART AI CALL: DETECT QUERY & ADJUST LENGTH ----------
def generate_user_reply(review, rating):
    """
    Detects if feedback is a query and adjusts response length:
    - Queries: up to 50 words (more detailed help)
    - Positive/Negative: up to 15 words (brief acknowledgment)
    """
    
    # Detect if this is a query
    is_question = is_query(review)
    
    if is_question:
        # QUERY: Allow longer, more helpful response
        prompt = f"""You are a helpful customer service assistant. Answer this customer question clearly and helpfully in 2-3 sentences (max 50 words).

Question: "{review}"

Your helpful answer:"""
        
        response = call_llm(
            prompt,
            USER_MODEL,
            max_tokens=100,
            temperature=0.6
        )
        
    else:
        # POSITIVE/NEGATIVE: Short response
        prompt = f"""You are a customer service assistant. Read this feedback and respond naturally in ONE sentence (max 15 words).

If positive: thank the user warmly
If negative: apologize sincerely

Feedback: "{review}"

Your response:"""
        
        response = call_llm(
            prompt,
            USER_MODEL,
            max_tokens=40,
            temperature=0.5
        )

    # Fallback logic
    if not response or len(response) < 5:
        if is_question:
            return "Thank you for reaching out! Our support team will assist you shortly."
        return "Thank you for your feedback. We appreciate you reaching out!"

    return response

# ---------- ADMIN INSIGHTS ----------
def generate_admin_insights(review, rating):
    prompt = f"""Analyze this feedback and return ONLY valid JSON in this exact format:

{{"category": "positive/negative/query", "summary": "brief summary here", "recommended_action": "action here"}}

Feedback: "{review}"

JSON:"""

    raw = call_llm(
        prompt,
        ADMIN_MODEL,
        max_tokens=150,
        temperature=0.3
    )

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
    except Exception as e:
        return "query", fallback_summary(review), fallback_action_generic()

# ---------- FALLBACKS ----------
def fallback_summary(review):
    return review[:80] + ("..." if len(review) > 80 else "")

def fallback_action_generic():
    return "Review feedback and take appropriate action."