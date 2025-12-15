import sqlite3
import pandas as pd
import streamlit as st 
from pathlib import Path 

# --- CRITICAL: Define DB path reliably relative to the app's root ---
DB_FILE = (Path(__file__).parent / "reviews.db").resolve()
DB_FILE_STR = str(DB_FILE)

# --- Define the table structure for initialization ---
TABLE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS reviews (
        rating INTEGER,
        review TEXT,
        ai_response TEXT,
        summary TEXT,
        recommended_action TEXT
    )
"""

def init_db():
    """Initializes the database file and table if they don't exist."""
    try:
        conn = sqlite3.connect(DB_FILE_STR) 
        c = conn.cursor()
        c.execute(TABLE_SCHEMA)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Error during DB initialization: {e}")

# Initialize the database file/table when the module is loaded
init_db()

@st.cache_data(ttl=600)
def load_reviews():
    """Loads all reviews from the SQLite database into a Pandas DataFrame."""
    try:
        conn = sqlite3.connect(DB_FILE_STR)
        # Load the data, ensure the connection is closed
        df = pd.read_sql_query("SELECT * FROM reviews", conn)
        conn.close()
        return df
    except Exception as e:
        # Crucial for preventing the 'NoneType' crash
        print(f"❌ Error loading reviews from DB: {e}")
        return pd.DataFrame() 

def save_review(rating, review, ai_response, summary, action):
    """Saves a new review record to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE_STR) 
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO reviews (rating, review, ai_response, summary, recommended_action)
            VALUES (?, ?, ?, ?, ?)
        ''', (rating, review, ai_response, summary, action))
        
        conn.commit()
        conn.close()
        
        # This forces the admin dashboard to refresh its data cache on next run
        load_reviews.clear()
        
        print(f"✅ Review saved to: {DB_FILE_STR}")

    except Exception as e:
        print(f"❌ Error saving review to DB: {e}")
