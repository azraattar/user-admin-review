import sqlite3
import pandas as pd
import os

# Set the path for the database file. 
# It's kept simple so it sits in the root of the app where it is accessible.
DB_FILE = "reviews.db"

def init_db():
    """Initializes the database and creates the reviews table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            rating INTEGER,
            review TEXT,
            ai_response TEXT,
            summary TEXT,
            recommended_action TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database file/table when the module is loaded
init_db()

def save_review(rating, review, ai_response, summary, action):
    """Saves a new review record to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO reviews (rating, review, ai_response, summary, recommended_action)
            VALUES (?, ?, ?, ?, ?)
        ''', (rating, review, ai_response, summary, action))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Review saved to: {DB_FILE}")

    except Exception as e:
        print("❌ Error saving review:", e)

def load_reviews():
    """Loads all reviews from the SQLite database into a Pandas DataFrame."""
    try:
        conn = sqlite3.connect(DB_FILE)
        # Use pandas to read the entire table into a DataFrame
        df = pd.read_sql_query("SELECT * FROM reviews", conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ Error loading reviews:", e)
        return pd.DataFrame()