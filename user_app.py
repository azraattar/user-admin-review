import streamlit as st
from ai_utils import generate_user_reply, generate_admin_insights
from data_utils import save_review

st.set_page_config(page_title="User Feedback", page_icon="⭐", layout="wide")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
.stApp { background-color: #f5f1e8; }
.stApp, .stApp * { color: #1a1a1a !important; }
header[data-testid="stHeader"] { display: none !important; }

.main {
    padding: 0rem 2rem 3rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.decorative-line {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
    gap: 1rem;
}
.decorative-line::before,
.decorative-line::after {
    content: '';
    height: 2px;
    width: 100px;
    background-color: #1a1a1a;
}
.decorative-line span {
    font-size: 1.5rem;
}

.rating-pills {
    display: flex;
    justify-content: center;
    margin: 1rem 0;
}
.rating-pill {
    padding: 0.5rem 1.5rem;
    border: 2px solid #1a1a1a;
    background-color: #ffffff;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.9rem;
}

.stButton > button {
    width: 100%;
    background-color: #f5f1e8;
    border: 2px solid #1a1a1a;
    height: 3.5em;
    font-size: 16px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background-color: #1a1a1a;
    color: #f5f1e8 !important;
}

.stTextArea textarea {
    border-radius: 0;
    border: 2px solid #1a1a1a;
    background-color: #fefdfb;
    font-size: 1rem;
    padding: 1rem;
}

.response-box {
    background-color: #fefdfb;
    border: 2px solid #1a1a1a;
    padding: 2rem;
    margin-top: 2rem;
    box-shadow: 8px 8px 0px #1a1a1a;
}
.response-box h3 {
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1rem;
}
.response-box p {
    font-size: 1.05rem;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# -------------------- DECORATIVE ELEMENTS --------------------
star_icon = """
<div style="text-align:center;margin-bottom:2rem;">
<svg width="60" height="60" viewBox="0 0 24 24" fill="none">
<path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02
L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
fill="#f5f1e8" stroke="#1a1a1a" stroke-width="2"/>
</svg>
</div>
"""

decorative_line = """
<div class="decorative-line">
<span>✂</span><span>✂</span><span>✂</span>
</div>
"""

# -------------------- HEADER --------------------
st.markdown(decorative_line, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown(star_icon, unsafe_allow_html=True)
    st.title("User Feedback")
    st.markdown(
        '<p style="text-align:center;color:#4a4a4a;font-size:1.1rem;">'
        'We value your opinion! Share your experience with us.</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    # -------------------- FORM --------------------
    st.markdown("#### Rate Your Experience")
    rating = st.slider("", 1, 5, 5)

    rating_labels = {
        1: "Poor",
        2: "Fair",
        3: "Good",
        4: "Very Good",
        5: "Excellent"
    }

    st.markdown(
        f'<div class="rating-pills"><div class="rating-pill">{rating_labels[rating]}</div></div>',
        unsafe_allow_html=True
    )

    st.markdown("#### Share Your Thoughts")
    review = st.text_area(
        "",
        placeholder="Tell us about your experience...",
        height=150,
        label_visibility="collapsed"
    )

    # -------------------- SUBMIT --------------------
    if st.button("Submit Feedback"):
        if review.strip() == "":
            st.warning("⚠️ Please write a review before submitting.")
        else:
            # 1️⃣ FAST USER RESPONSE
            with st.spinner("Responding..."):
                user_reply = generate_user_reply(review, rating)

            st.success("✅ Thank you for your valuable feedback!")

            st.markdown(f"""
            <div class="response-box">
                <h3>Our Response</h3>
                <p>{user_reply}</p>
            </div>
            """, unsafe_allow_html=True)

            # 2️⃣ ADMIN PROCESSING (SECONDARY)
            with st.spinner("Finalizing feedback..."):
                summary, action = generate_admin_insights(review, rating)

                save_review(
                    rating,
                    review,
                    user_reply,
                    summary,
                    action
                )

st.markdown(decorative_line, unsafe_allow_html=True)
