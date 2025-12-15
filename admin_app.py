import streamlit as st
from data_utils import load_reviews
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

# -------------------- PERFORMANCE FIX: Caching the Charts --------------------
@st.cache_data
def generate_charts(data: pd.DataFrame):
    """Generates and returns the Plotly figures based on the input data."""
    
    rating_counts = data["rating"].value_counts().sort_index()

    # --- PIE CHART LOGIC ---
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
    
    # --- BAR CHART LOGIC ---
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
    
    return fig_pie, fig_bar


# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
.stApp { background-color: #f5f1e8; }
.stApp, .stApp * { color: #1a1a1a !important; }
header[data-testid="stHeader"] { display: none !important; }
.main .block-container { padding-top: 2rem !important; }
... (rest of your beautiful CSS remains here) ...
</style>
""", unsafe_allow_html=True)


# -------------------- DECORATIVE ELEMENTS --------------------
dashboard_icon = """
<div class="dashboard-icon">
... (your SVG code remains here) ...
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
data = load_reviews() # This call is now fast because it is cached in data_utils.py


if data.empty:
    st.info("No feedback yet. Check back soon!")
else:
    # -------------------- METRICS --------------------
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    # ... (Metrics calculation and display code remains unchanged) ...
    
    # -------------------- CHARTS --------------------
    st.markdown("### Analytics")
    chart_col1, chart_col2 = st.columns(2)

    # 💡 FIX: Call the cached function to get the charts
    fig_pie, fig_bar = generate_charts(data) 
    
    with chart_col1:
        st.markdown("#### Rating Distribution")
        st.plotly_chart(fig_pie, use_container_width=True, key="pie")

    with chart_col2:
        st.markdown("#### Rating Frequency")
        st.plotly_chart(fig_bar, use_container_width=True, key="bar")

    # -------------------- FEEDBACK EXPLORER --------------------
    # ... (Rest of your original code for radio buttons and review cards remains unchanged) ...

st.markdown(decorative_line, unsafe_allow_html=True)
