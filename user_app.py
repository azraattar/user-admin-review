import streamlit as st
from ai_utils import generate_user_reply, summarize_review, recommend_action
from data_utils import save_review

st.set_page_config(page_title="User Feedback", page_icon="⭐", layout="wide")

# Custom CSS inspired by the portfolio design
st.markdown("""
    <style>
    /* Clean beige background */
    .stApp {
        background-color: #f5f1e8;
    }
    
    /* Main container */
    .main {
        padding: 0rem 2rem 3rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Force all text to be black */
    .stApp, .stApp * {
        color: #1a1a1a !important;
    }
    
    /* Override Streamlit's default white header */
    header {
        background-color: transparent !important;
    }
    
    .main > div:first-child {
        padding-top: 0 !important;
    }
    
    /* Header section */
    .header-section {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
    }
    
    .header-section h1 {
        font-size: 3rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
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
    
    /* Feedback card */
    
    
    /* Section headers */
    h4 {
        color: #1a1a1a;
        font-weight: 600;
        font-size: 1.2rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Submit button - Fixed to show text at all times */
    .stButton>button {
        width: 100%;
        background-color: #f5f1e8;
        color: #1a1a1a !important;
        height: 3.5em;
        border-radius: 0;
        font-size: 16px;
        font-weight: 600;
        border: 2px solid #1a1a1a;
        margin-top: 2rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1a1a1a;
        color: #f5f1e8 !important;
        border: 2px solid #1a1a1a;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 0;
        border: 2px solid #1a1a1a;
        background-color: #fefdfb;
        font-size: 1rem;
        padding: 1rem;
        color: #1a1a1a;
    }
    
    .stTextArea textarea:focus {
        border-color: #1a1a1a;
        box-shadow: 4px 4px 0px #1a1a1a;
    }
    
    /* Slider styling */
    .stSlider {
        padding: 1.5rem 0;
    }
    
    .stSlider label {
        color: #1a1a1a !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        color: #1a1a1a;
    }
    
    /* Rating pills */
    .rating-pills {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
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
    
    /* Response box */
    .response-box {
        background-color: #fefdfb;
        border: 2px solid #1a1a1a;
        border-radius: 0;
        padding: 2rem;
        margin-top: 2rem;
        color: #1a1a1a !important;
        box-shadow: 8px 8px 0px #1a1a1a;
    }
    
    .response-box h3 {
        color: #1a1a1a !important;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .response-box p {
        color: #1a1a1a !important;
        line-height: 1.6;
    }
    
    /* Success message */
    .stSuccess {
        background-color: #d4edda;
        border: 2px solid #1a1a1a;
        border-radius: 0;
        color: #1a1a1a;
    }
    
    /* Warning message */
    .stWarning {
        background-color: #fff3cd;
        border: 2px solid #1a1a1a;
        border-radius: 0;
        color: #1a1a1a;
    }
    
    /* Info message */
    .stInfo {
        background-color: #fefdfb;
        border: 2px solid #1a1a1a;
        border-radius: 0;
        color: #1a1a1a;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem;
    }
    
    /* Hide Streamlit header */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    .main .block-container {
        padding-top: 2rem !important;
    }
    
    /* Star icon */
    .star-icon {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Title */
    h1 {
        text-align: center;
        color: #1a1a1a;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #4a4a4a;
        font-size: 1.1rem;
        margin-bottom: 0;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background-color: #1a1a1a;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Star icon SVG (simple black outline style)
star_icon = """
<div class="star-icon">
    <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" 
              fill="#f5f1e8" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
</div>
"""

# Decorative line
decorative_line = """
<div class="decorative-line">
    <span>✂</span>
    <span>✂</span>
    <span>✂</span>
</div>
"""

# Header section
st.markdown(decorative_line, unsafe_allow_html=True)

# Create centered layout
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    
    # Header with icon
    st.markdown(star_icon, unsafe_allow_html=True)
    st.title("User Feedback")
    st.markdown('<p class="subtitle">We value your opinion! Share your experience with us.</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Rating section
    st.markdown("#### Rate Your Experience")
    rating = st.slider("", 1, 5, 5, help="1 = Poor, 5 = Excellent")
    
    # Display rating label only (removed emojis)
    rating_labels = {1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent"}
    
    st.markdown(f'<div class="rating-pills"><div class="rating-pill">{rating_labels[rating]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("#### Share Your Thoughts")
    review = st.text_area("", placeholder="Tell us about your experience...", height=150, label_visibility="collapsed")
    
    # Submit button
    if st.button("Submit Feedback"):
        if review.strip() == "":
            st.warning("⚠️ Please write a review before submitting.")
        else:
            with st.spinner("Processing your feedback..."):
                ai_reply = generate_user_reply(review, rating)
                summary = summarize_review(review)
                action = recommend_action(review, rating)
                
                save_review(rating, review, ai_reply, summary, action)
            
            st.success("✅ Thank you for your valuable feedback!")
            
            # Display AI response inside the response box
            st.markdown(f"""
            <div class="response-box">
                <h3>Our Response</h3>
                <p>{ai_reply}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(decorative_line, unsafe_allow_html=True)