import streamlit as st
from data_utils import load_reviews
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")


# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
.stApp { background-color: #f5f1e8; }
.stApp, .stApp * { color: #1a1a1a !important; }
header[data-testid="stHeader"] { display: none !important; }
.main .block-container { padding-top: 2rem !important; }


.decorative-line {
    display: flex; 
    align-items: center;
    justify-content: center; 
    gap: 1rem; 
    margin: 2rem 0;
}
.decorative-line::before, .decorative-line::after {
    content: ''; 
    height: 2px; 
    width: 150px; 
    background-color: #1a1a1a;
}
.decorative-line span { font-size: 1.5rem; }


.dashboard-card {
    background: #ffffff;
    border: 2px solid #1a1a1a;
    border-radius: 0;
    padding: 2rem;
    box-shadow: 8px 8px 0px #1a1a1a;
    margin-bottom: 2rem;
}


.metric-card {
    background: #fefdfb;
    border: 2px solid #1a1a1a;
    border-radius: 0;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 6px 6px 0px #1a1a1a;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}


.metric-title {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
    color: #4a4a4a;
    margin-bottom: 0.8rem;
}


.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1;
}


/* Only apply to actual plotly charts */
div[data-testid="stPlotlyChart"] > div {
    background: #ffffff;
    border: 2px solid #1a1a1a;
    border-radius: 0;
    padding: 1.5rem;
    box-shadow: 6px 6px 0px #1a1a1a;
    margin-bottom: 1rem;
}


/* Column alignment */
[data-testid="column"] {
    padding: 0 0.5rem;
}


[data-testid="column"]:first-child {
    padding-left: 0;
}


[data-testid="column"]:last-child {
    padding-right: 0;
}


/* Section headers */
h1 {
    text-align: center;
    color: #1a1a1a;
    font-weight: 700;
    font-size: 2.5rem;
    margin-bottom: 1rem;
}


h3 {
    color: #1a1a1a;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2rem;
    margin-bottom: 1rem;
}


h4 {
    color: #1a1a1a;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1rem;
    font-size: 1rem;
}


/* Radio button styling - Pinterest style */
.stRadio {
    background-color: transparent !important;
}


.stRadio > div {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}


.stRadio > div > label {
    background-color: #ffffff !important;
    border: 2px solid #1a1a1a !important;
    border-radius: 0 !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-size: 0.85rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 3px 3px 0px #1a1a1a !important;
    margin-bottom: 0.5rem !important;
}


.stRadio > div > label:hover {
    background-color: #1a1a1a !important;
    color: #f5f1e8 !important;
    transform: translateY(-2px);
    box-shadow: 5px 5px 0px #1a1a1a !important;
}


.stRadio > div > label[data-selected="true"] {
    background-color: #1a1a1a !important;
    color: #f5f1e8 !important;
    box-shadow: 5px 5px 0px #4a4a4a !important;
}


/* Info styling */
.stInfo {
    background-color: #fefdfb;
    border: 2px solid #1a1a1a;
    border-radius: 0;
    box-shadow: 6px 6px 0px #1a1a1a;
}


/* Dashboard icon */
.dashboard-icon {
    text-align: center;
    margin-bottom: 1rem;
}


/* Table section header - Pinterest board header style */
.table-section-header {
    background-color: #1a1a1a;
    color: #f5f1e8 !important;
    padding: 1.2rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: -2rem -2rem 1.5rem -2rem;
    text-align: center;
    font-size: 1rem;
}


/* View selector label */
.view-label {
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    color: #4a4a4a;
}


/* Review card styling */
.review-card {
    background: #fefdfb;
    border: 2px solid #1a1a1a;
    border-radius: 0;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 4px 4px 0px #1a1a1a;
    transition: all 0.3s ease;
}


.review-card:hover {
    transform: translateY(-2px);
    box-shadow: 6px 6px 0px #1a1a1a;
}


.review-rating {
    display: inline-block;
    background: #1a1a1a;
    color: #f5f1e8 !important;
    padding: 0.5rem 1rem;
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    box-shadow: 3px 3px 0px #4a4a4a;
}


.review-content {
    font-size: 1.05rem;
    line-height: 1.8;
    color: #1a1a1a !important;
}
</style>
""", unsafe_allow_html=True)


# -------------------- DECORATIVE ELEMENTS --------------------
dashboard_icon = """
<div class="dashboard-icon">
    <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="3" width="7" height="7" stroke="#1a1a1a" stroke-width="2" fill="#f5f1e8"/>
        <rect x="14" y="3" width="7" height="7" stroke="#1a1a1a" stroke-width="2" fill="#f5f1e8"/>
        <rect x="3" y="14" width="7" height="7" stroke="#1a1a1a" stroke-width="2" fill="#f5f1e8"/>
        <rect x="14" y="14" width="7" height="7" stroke="#1a1a1a" stroke-width="2" fill="#f5f1e8"/>
    </svg>
</div>
"""


decorative_line = """
<div class="decorative-line">
    <span>★</span><span>★</span><span>★</span>
</div>
"""


st.markdown(decorative_line, unsafe_allow_html=True)
st.markdown(dashboard_icon, unsafe_allow_html=True)
st.title("Admin Dashboard")
st.markdown(decorative_line, unsafe_allow_html=True)


# -------------------- LOAD DATA --------------------
data = load_reviews()


if data.empty:
    st.info("No feedback yet. Check back soon!")
else:
    # -------------------- METRICS --------------------
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)


    avg_rating = round(data["rating"].mean(), 2)
    total_reviews = len(data)
    positive_reviews = len(data[data["rating"] >= 4])
    negative_reviews = len(data[data["rating"] <= 2])


    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Rating</div>
            <div class="metric-value">{avg_rating}</div>
        </div>
        """, unsafe_allow_html=True)


    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Reviews</div>
            <div class="metric-value">{total_reviews}</div>
        </div>
        """, unsafe_allow_html=True)


    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Positive Reviews</div>
            <div class="metric-value">{positive_reviews}</div>
        </div>
        """, unsafe_allow_html=True)


    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Negative Reviews</div>
            <div class="metric-value">{negative_reviews}</div>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)


    # -------------------- CHARTS --------------------
    st.markdown("### Analytics")
    chart_col1, chart_col2 = st.columns(2)


    rating_counts = data["rating"].value_counts().sort_index()


    with chart_col1:
        st.markdown("#### Rating Distribution")
        fig_pie = px.pie(
            values=rating_counts.values,
            names=rating_counts.index,
            title="",
            color_discrete_sequence=['#1a1a1a', '#4a4a4a', '#6a6a6a', '#8a8a8a', '#aaaaaa']
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a1a1a', size=12),
            showlegend=True,
            margin=dict(t=10, b=10, l=10, r=10),
            height=350
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="pie")


    with chart_col2:
        st.markdown("#### Rating Frequency")
        fig_bar = go.Figure(
            data=[go.Bar(
                x=rating_counts.index, 
                y=rating_counts.values,
                marker_color='#1a1a1a',
                marker_line_color='#1a1a1a',
                marker_line_width=2,
                text=rating_counts.values,
                textposition='outside'
            )]
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a1a1a', size=12),
            height=350,
            xaxis_title="Rating",
            yaxis_title="Count",
            showlegend=False,
            xaxis=dict(gridcolor='#e0e0e0', tickmode='linear'),
            yaxis=dict(gridcolor='#e0e0e0'),
            margin=dict(t=10, b=40, l=40, r=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="bar")


    # -------------------- FEEDBACK EXPLORER --------------------
    st.markdown("### Feedback Explorer")
    st.markdown('<p class="view-label">Select View</p>', unsafe_allow_html=True)


    view = st.radio(
        "",
        ["User Reviews", "AI Responses", "Summaries", "Recommended Actions"],
        horizontal=True,
        label_visibility="collapsed"
    )


    # Normalize rating display once
    data = data.copy()
    data["Rating"] = data["rating"].apply(lambda x: f"{x} ★")


    if view == "User Reviews":
        display_df = data[["Rating", "review"]].rename(
            columns={"review": "User Review"}
        )
        header_text = "User Reviews"


    elif view == "AI Responses":
        display_df = data[["Rating", "ai_response"]].rename(
            columns={"ai_response": "AI Response to User"}
        )
        header_text = "AI Responses"


    elif view == "Summaries":
        display_df = data[["Rating", "summary"]].rename(
            columns={"summary": "AI Summary"}
        )
        header_text = "Review Summaries"


    else:  # Recommended Actions
        display_df = data[["Rating", "recommended_action"]].rename(
            columns={"recommended_action": "Recommended Action"}
        )
        header_text = "Recommended Actions"


    # ----------- RENDER AS STYLED CARDS -----------
    st.markdown(f'<h4 style="text-align: center; margin-top: 2rem; margin-bottom: 1.5rem;">{header_text}</h4>', unsafe_allow_html=True)


    for _, row in display_df.iterrows():
        st.markdown(f"""
        <div class="review-card">
            <div class="review-rating">{row['Rating']}</div>
            <div class="review-content">{row.iloc[1]}</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown(decorative_line, unsafe_allow_html=True)
