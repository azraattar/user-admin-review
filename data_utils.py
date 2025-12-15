import pandas as pd
import streamlit as st 
# We no longer need: import sqlite3, import os, import Path

# --- Supabase Integration using st.connection ---

# data_utils.py

def get_connection():
    """
    Initializes and returns the Streamlit connection object for Supabase
    using the full connection URI from the 'DATABASE_URL' secret.
    """
    return st.connection("supabase_db", type="sql", url=st.secrets["DATABASE_URL"])

def save_review(rating, review, ai_response, summary, action):
    """Saves a new review record to the Supabase database."""
    try:
        conn = get_connection()
        
        # Use a parameterized query to securely insert data
        conn.query(
            """
            INSERT INTO reviews (rating, review, ai_response, summary, recommended_action)
            VALUES (%(rating)s, %(review)s, %(ai_response)s, %(summary)s, %(action)s);
            """,
            params={
                "rating": rating,
                "review": review,
                "ai_response": ai_response,
                "summary": summary,
                "action": action
            },
            ttl=0 # Do not cache this write operation
        )
        
        # 💡 FIX: Clear the data cache to ensure the Admin Dashboard gets the new data immediately
        load_reviews.clear()
        
        print("✅ Review saved to Supabase.")

    except Exception as e:
        print(f"❌ Error saving review to Supabase: {e}")

@st.cache_data(ttl=600)
def load_reviews() -> pd.DataFrame:
    """Loads all reviews from Supabase into a Pandas DataFrame."""
    try:
        conn = get_connection()
        
        # Read the entire table into a DataFrame
        df = conn.query("SELECT * FROM reviews", ttl=600)
        
        # Ensure column names are consistent (st.connection often returns lowercase)
        df.columns = [c.lower() for c in df.columns] 
        
        return df
    except Exception as e:
        print(f"❌ Error loading reviews from Supabase: {e}")
        # Always return an empty DataFrame on failure to prevent the crash
        return pd.DataFrame() 


# The init_db() function is no longer strictly needed in code 
# because you set up the table manually on Supabase.
