import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "reviews.csv")

def save_review(rating, review, ai_response, summary, action):
    new_row = {
        "rating": rating,
        "review": review,
        "ai_response": ai_response,
        "summary": summary,
        "recommended_action": action
    }

    try:
        if os.path.exists(FILE_PATH):
            df = pd.read_csv(FILE_PATH)
        else:
            df = pd.DataFrame(columns=new_row.keys())

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(FILE_PATH, index=False)

        print("✅ Review saved to:", FILE_PATH)

    except Exception as e:
        print("❌ Error saving review:", e)

def load_reviews():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    return pd.DataFrame()
