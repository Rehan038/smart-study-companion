import streamlit as st
from database.db import get_roadmaps, save_feedback

def show_feedback_page():
    """Feedback form for Students."""
    st.header("💬 Roadmap Feedback")
    maps = get_roadmaps()
    if not maps:
        st.info("No roadmaps generated yet. Go to 'Generate Roadmap' first!")
        return
        
    options = {f"[{r['id']}] {r['topic']}": r["id"] for r in maps}
    sel = st.selectbox("Select Roadmap to review", list(options.keys()))
    
    with st.form("feedback_form"):
        rating = st.slider("Rate your roadmap (1-5)", 1, 5, 3)
        comment = st.text_area("Observations or suggestions")
        if st.form_submit_button("Submit Feedback"):
            save_feedback(options[sel], rating, comment)
            st.success("Feedback submitted! Thank you.")
