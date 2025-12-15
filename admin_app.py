import streamlit as st
from data_utils import load_reviews
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

# 🚨 RECOMMENDED FIX: Cache the complex chart generation
@st.cache_data
def generate_charts(data: pd.DataFrame):
    """Generates and returns the Plotly figures based on the input data."""
    
    rating_counts = data["rating"].value_counts().sort_index()

    # --- PIE CHART ---
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
    
    # --- BAR CHART ---
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

# -------------------- CUSTOM CSS (CSS is omitted for brevity but remains the same) --------------------
# ... (all your existing CSS and decorative elements code) ...

# -------------------- LOAD DATA --------------------
data = load_reviews() # This is now fast because it's cached!


if data.empty:
    st.info("No feedback yet. Check back soon!")
else:
    # -------------------- METRICS --------------------
    # ... (Metrics code is unchanged) ...

    # -------------------- CHARTS --------------------
    st.markdown("### Analytics")
    
    # 💡 FIX: Generate charts using the cached function
    fig_pie, fig_bar = generate_charts(data) 
    
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Rating Distribution")
        st.plotly_chart(fig_pie, use_container_width=True, key="pie")


    with chart_col2:
        st.markdown("#### Rating Frequency")
        st.plotly_chart(fig_bar, use_container_width=True, key="bar")

    # -------------------- FEEDBACK EXPLORER (Rest of the code is unchanged) --------------------
    # ...
