import sqlite3
import pandas as pd
import os
# 🚨 FIX 1: Import Streamlit for caching
import streamlit as st 

# Set the path for the database file. 
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
        
        # 🚨 FIX 2: Clear the cache so the Admin Dashboard gets the new data immediately
        load_reviews.clear()
        
        print(f"✅ Review saved to: {DB_FILE}")

    except Exception as e:
        print("❌ Error saving review:", e)

# 🚨 FIX 3: Add the cache decorator to prevent slow dashboard reloading
@st.cache_data(ttl=600) # Cache for 10 minutes
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
