# data_utils.py
import pandas as pd
import streamlit as st
from sqlalchemy import text

def get_connection():
    return st.connection("supabase_db", type="sql")

def save_review(rating: int, review: str, ai_response: str, summary: str, action: str):
    conn = get_connection()
    sql = text("""
        INSERT INTO public.reviews (rating, review, ai_response, summary, recommended_action)
        VALUES (:rating, :review, :ai_response, :summary, :action)
    """)
    with conn.session as session:
        session.execute(sql, {
            "rating": int(rating),
            "review": review,
            "ai_response": ai_response,
            "summary": summary,
            "action": action,
        })
        session.commit()

def load_reviews() -> pd.DataFrame:
    conn = get_connection()
    df = conn.query(
        """
        SELECT rating, review, ai_response, summary, recommended_action
        FROM public.reviews
        ORDER BY id DESC;
        """,
        ttl=0,  # always fresh (turn to 600 later)
    )
    df.columns = [c.lower() for c in df.columns]
    return df
