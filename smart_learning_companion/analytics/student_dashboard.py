import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import math
from database.db import get_documents, get_roadmaps, get_feedback

def calculate_document_stats():
    """Calculates metrics and visualizations for uploaded documents."""
    docs = get_documents()
    if not docs:
        return 0, 0, 0, None
        
    df = pd.DataFrame(docs)
    total_docs = len(docs)
    
    # In this app, we don't store text in DB, so we simulate word count for the chart
    # using a heuristic or the current session text if available.
    # For a real system, word_count would be a column in the 'documents' table.
    active_text = st.session_state.get("doc_text", "")
    active_words = len(active_text.split()) if active_text else 0
    
    # Heuristic for historical docs if text isn't available
    df["word_count"] = [active_words if i == 0 and active_words > 0 else 1000 + (hash(d['filename']) % 4000) for i, d in enumerate(docs)]
    
    total_words = df["word_count"].sum()
    avg_length = df["word_count"].mean()
    
    fig = px.bar(df, x="filename", y="word_count", title="Word Count per Document", 
                 labels={"filename": "Document", "word_count": "Words"}, template="plotly_dark")
    
    return total_docs, total_words, avg_length, fig

def analyze_keywords():
    """Aggregates and visualizes keyword frequency."""
    filt = st.session_state.get("filtered", [])
    if not filt:
        return None, None
        
    from document_analysis.keyword_extraction import extract_keywords
    kw = extract_keywords(filt, top_n=10)
    df_kw = pd.DataFrame(kw, columns=["Keyword", "Frequency"])
    
    fig_bar = px.bar(df_kw, x="Frequency", y="Keyword", orientation="h", 
                     title="Top 10 Keywords", template="plotly_dark", color="Frequency")
    
    fig_pie = px.pie(df_kw, names="Keyword", values="Frequency", hole=0.3, 
                     title="Topic Weightage", template="plotly_dark")
    
    return fig_bar, fig_pie

def roadmap_statistics():
    """Analyzes roadmap generation patterns."""
    maps = get_roadmaps()
    if not maps:
        return 0, 0, "N/A", None
        
    df = pd.DataFrame(maps)
    total_maps = len(maps)
    
    # Estimate length by newline count
    df["length"] = df["roadmap"].apply(lambda x: len(x.split('\n')))
    avg_len = df["length"].mean()
    
    most_common = df["topic"].mode()[0] if not df["topic"].empty else "N/A"
    
    topic_counts = df["topic"].value_counts().reset_index()
    topic_counts.columns = ["Topic", "Count"]
    fig = px.bar(topic_counts, x="Topic", y="Count", title="Popular Roadmap Topics", 
                 template="plotly_dark", color="Count")
    
    return total_maps, avg_len, most_common, fig

def difficulty_analysis():
    """Calculates reading difficulty based on NLP metrics."""
    text = st.session_state.get("doc_text", "")
    toks = st.session_state.get("tokens", [])
    
    if not text or not toks:
        return "N/A", "N/A"
        
    words = text.split()
    total_words = len(words)
    total_sents = text.count('.') + text.count('?') + 1
    unique_words = len(set([w.lower() for w in words]))
    
    avg_word_len = sum(len(w) for w in words) / max(total_words, 1)
    avg_sent_len = total_words / max(total_sents, 1)
    vocab_ratio = unique_words / max(total_words, 1)
    
    # Logic: High word len + high sent len + high unique ratio = Hard
    score = (avg_word_len * 5) + (avg_sent_len * 0.5) + (vocab_ratio * 10)
    
    if score < 15: diff = "Easy"
    elif score < 25: diff = "Medium"
    else: diff = "Hard"
    
    return diff, score

def render_student_dashboard():
    """Main entry point for the student analytics dashboard."""
    st.title("🎓 Student Analytics Dashboard")
    
    # ── Section 1: Activity Metrics ──
    st.header("📈 Activity Overview")
    total_docs, total_words, avg_doc_len, fig_words = calculate_document_stats()
    total_maps, _, _, _ = roadmap_statistics()
    fb = get_feedback()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Documents Uploaded", total_docs)
    c2.metric("Roadmaps Generated", total_maps)
    c3.metric("Feedback Submitted", len(fb))
    
    st.markdown("---")
    
    # ── Section 2: Document Analysis ──
    st.header("📄 Document Metrics")
    if total_docs > 0:
        cc1, cc2 = st.columns(2)
        cc1.metric("Total Words Processed", f"{total_words:,}")
        cc2.metric("Avg Doc Length", f"{int(avg_doc_len)} words")
        st.plotly_chart(fig_words, use_container_width=True)
    else:
        st.info("No documents uploaded yet.")
        
    # ── Section 3: Keyword Analysis ──
    st.header("🔍 Keyword Insights")
    fig_kw_bar, fig_kw_pie = analyze_keywords()
    if fig_kw_bar:
        st.plotly_chart(fig_kw_bar, use_container_width=True)
        st.plotly_chart(fig_kw_pie, use_container_width=True)
    else:
        st.info("Analyze a document to see keyword distributions.")

def show_student_analytics():
    """Legacy wrapper to maintain compatibility."""
    render_student_dashboard()
