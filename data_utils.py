import sqlite3
import pandas as pd
import streamlit as st 
from pathlib import Path 

# 1. Define DB path reliably for cloud environments
DB_FILE = (Path(__file__).parent / "reviews.db").resolve()
DB_FILE_STR = str(DB_FILE)

def init_db():
    """Initializes the database and creates the reviews table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE_STR) 
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

@st.cache_data(ttl=600)
def load_reviews():
    """Loads all reviews from the SQLite database into a Pandas DataFrame."""
    try:
        conn = sqlite3.connect(DB_FILE_STR)
        df = pd.read_sql_query("SELECT * FROM reviews", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"❌ Error loading reviews from DB: {e}")
        # 2. CRITICAL FIX: Return an empty DataFrame, NOT None
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
        
        # 3. Clear cache so Admin Dashboard sees the new data on next load
        load_reviews.clear()
        
        print(f"✅ Review saved to: {DB_FILE_STR}")

    except Exception as e:
        print(f"❌ Error saving review to DB: {e}")
