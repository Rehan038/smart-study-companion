import pandas as pd
import plotly.express as px
import streamlit as st
from database.db import get_documents, get_roadmaps, get_feedback, get_user_count

def system_usage_metrics():
    """Section 1: System Metrics."""
    st.header("📊 System Usage Metrics")
    c1, c2, c3, c4 = st.columns(4)
    
    total_users = get_user_count()
    total_docs = len(get_documents())
    total_maps = len(get_roadmaps())
    total_fb = len(get_feedback())
    
    c1.metric("Total Users", total_users)
    c2.metric("Total Documents Uploaded", total_docs)
    c3.metric("Total Roadmaps Generated", total_maps)
    c4.metric("Total Feedback Entries", total_fb)

def topic_popularity_analysis():
    """Section 2: Most Studied Topics."""
    st.header("🔝 Most Studied Topics")
    maps = get_roadmaps()
    if not maps:
        st.info("No roadmap data available.")
        return
        
    df = pd.DataFrame(maps)
    topic_counts = df["topic"].value_counts().reset_index()
    topic_counts.columns = ["Topic", "Frequency"]
    
    fig = px.bar(topic_counts, x="Topic", y="Frequency", 
                 title="Popular Roadmap Topics",
                 labels={"Frequency": "Number of Roadmaps"},
                 template="plotly_dark",
                 color="Frequency",
                 color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)

def concept_trend_analysis():
    """Section 3: Concept Trends Across Documents."""
    st.header("🔍 Concept Trends")
    docs = get_documents()
    all_kws = []
    for d in docs:
        if d.get("keywords"):
             kws = [k.strip() for k in d["keywords"].split(",") if k.strip()]
             all_kws.extend(kws)
    
    if not all_kws:
        st.info("No concept data available yet.")
        return
        
    df_kw = pd.DataFrame(all_kws, columns=["Concept"])
    kw_counts = df_kw["Concept"].value_counts().head(15).reset_index()
    kw_counts.columns = ["Concept", "Occurrences"]
    
    fig = px.bar(kw_counts, x="Occurrences", y="Concept", orientation='h',
                 title="Most Frequent Concepts Across Documents",
                 labels={"Occurrences": "Count"},
                 template="plotly_dark",
                 color="Occurrences",
                 color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

def feedback_statistics():
    """Section 4: Feedback Analysis."""
    st.header("⭐ Feedback Analytics")
    fb = get_feedback()
    if not fb:
        st.info("No feedback entries available.")
        return
        
    df = pd.DataFrame(fb)
    
    col1, col2 = st.columns([1, 2])
    avg_rating = df["rating"].mean()
    col1.metric("Average Rating", f"{avg_rating:.2f} / 5.0")
    
    # Rating Distribution Histogram
    fig_hist = px.histogram(df, x="rating", nbins=5, 
                            title="Rating Distribution",
                            labels={"rating": "Stars"},
                            template="plotly_dark",
                            color_discrete_sequence=["#fbbf24"])
    fig_hist.update_layout(bargap=0.2)
    col2.plotly_chart(fig_hist, use_container_width=True)
    
    st.subheader("Detailed Feedback Table")
    st.table(df[["topic", "rating", "comment"]])

def upload_trend_analysis():
    """Section 5: Content Upload Trends."""
    st.header("📅 Content Upload Trends")
    docs = get_documents()
    if not docs:
        st.info("No upload history available.")
        return
        
    df = pd.DataFrame(docs)
    # Ensure correct datetime conversion
    df["upload_day"] = pd.to_datetime(df["upload_time"], format='mixed').dt.date
    trend = df.groupby("upload_day").size().reset_index(name="Uploads")
    
    fig = px.line(trend, x="upload_day", y="Uploads", 
                  title="Document Uploads Per Day",
                  labels={"upload_day": "Date"},
                  template="plotly_dark",
                  markers=True)
    fig.update_traces(line_color="#10b981")
    st.plotly_chart(fig, use_container_width=True)

def render_admin_dashboard():
    """Final entry point for the Admin Dashboard."""
    st.title("🛡️ Admin Analytics Control Center")
    st.markdown("---")
    
    system_usage_metrics()
    st.markdown("---")
    
    topic_popularity_analysis()
    st.markdown("---")
    
    concept_trend_analysis()
    st.markdown("---")
    
    feedback_statistics()
    st.markdown("---")
    
    upload_trend_analysis()

def show_admin_analytics():
    """Compatibility wrapper."""
    render_admin_dashboard()
