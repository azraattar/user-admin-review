import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"

def generate_user_reply(review, rating):
    prompt = f"""
You are a polite customer support assistant.
Respond kindly to this review.

Rating: {rating}
Review: {review}
"""
    return ask_ollama(prompt)

def summarize_review(review):
    prompt = f"Summarize this review in one sentence:\n{review}"
    return ask_ollama(prompt)

def recommend_action(review, rating):
    prompt = f"""
Based on the following review and rating ({rating}),
suggest a recommended business action.

Review: {review}
"""
    return ask_ollama(prompt)

def ask_ollama(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        return response.json()["response"].strip()
    else:
        return "AI service unavailable."
