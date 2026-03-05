import streamlit as st
from database.db import initialize_database, save_document
from auth.login import show_login_page
from document_analysis.pdf_reader import extract_text_from_pdf
from document_analysis.text_preprocessing import clean_text, tokenize_text, remove_stopwords
from document_analysis.summarizer import generate_summary
from roadmap.roadmap_generator import generate_roadmap
from roadmap.feedback import show_feedback_page
from analytics.student_dashboard import show_student_analytics
from analytics.admin_dashboard import show_admin_analytics
from admin.admin_panel import show_admin_panel

# ── Init ──
if "db_init" not in st.session_state:
    initialize_database()
    st.session_state["db_init"] = True

def main():
    if not st.session_state.get("logged_in"):
        show_login_page()
        return

    role = st.session_state["role"]
    username = st.session_state["username"]

    st.sidebar.title(f"🎓 Smart Learning")
    st.sidebar.write(f"Logged as: **{username}** ({role})")

    if role == "student":
        nav = st.sidebar.radio("Navigation", [
            "Upload Document", 
            "Generate Summary", 
            "Generate Roadmap", 
            "Submit Feedback", 
            "Student Analytics"
        ])
        
        if nav == "Upload Document":
            st.header("📂 Document Upload")
            f = st.file_uploader("Choose a study PDF", type=["pdf"])
            if f:
                from pathlib import Path
                up_dir = Path("data/uploads")
                up_dir.mkdir(parents=True, exist_ok=True)
                path = up_dir / f.name
                with open(path, "wb") as fh: fh.write(f.getbuffer())
                try:
                    # ── Extraction ──
                    text = extract_text_from_pdf(path)
                    st.session_state["doc_text"] = text
                    st.session_state["doc_name"] = f.name
                    save_document(f.name)
                    
                    # ── Auto-Analysis ──
                    with st.spinner("Analyzing document..."):
                        cleaned = clean_text(text)
                        tokens = tokenize_text(cleaned)
                        filtered = remove_stopwords(tokens)
                        st.session_state["tokens"] = tokens
                        st.session_state["filtered"] = filtered
                        
                        # Save keywords to DB and session for Roadmap Weaving
                        from database.db import update_document_keywords
                        from document_analysis.keyword_extraction import extract_keywords
                        extracted = [k[0] for k in extract_keywords(filtered, top_n=10)]
                        st.session_state["doc_keywords"] = extracted
                        kw_str = ",".join(extracted)
                        update_document_keywords(f.name, kw_str)
                        
                    st.success("Document uploaded and analyzed automatically!")
                    st.info(f"**Snippet:** {text[:300]}...")
                except Exception as e: st.error(str(e))
        
        elif nav == "Generate Summary":
            st.header("📝 Summarizer")
            if "doc_text" not in st.session_state: st.warning("Upload a doc first")
            else:
                c = st.slider("Sentences", 3, 15, 5)
                if st.button("Generate"):
                    s = generate_summary(st.session_state["doc_text"], c)
                    st.info(s)
        
        elif nav == "Generate Roadmap":
            st.header("🗺️ Roadmap Builder")
            t = st.text_input("Topic (e.g. Python, Machine Learning)")
            kw = st.session_state.get("doc_keywords")
            if st.button("Create Plan") and t:
                try:
                    from roadmap.roadmap_generator import get_graph_fig
                    r_list, G = generate_roadmap(t, pdf_keywords=kw)
                    st.success(f"Intel Roadmap generated for {t}")
                    
                    # Display Text
                    for item in r_list:
                        st.write(f"**Week {item['week']}**: {item['concept']} ({item['hours']} hrs)")
                    
                    # Display Graph
                    if G:
                        st.subheader("Learning Path Visualization")
                        st.plotly_chart(get_graph_fig(G), use_container_width=True)
                except Exception as e: st.error(str(e))
        
        elif nav == "Submit Feedback":
            show_feedback_page()
        
        elif nav == "Student Analytics":
            show_student_analytics()

    elif role == "admin":
        nav = st.sidebar.radio("Navigation", ["Admin Dashboard"])
        
        if nav == "Admin Dashboard":
            show_admin_panel()

    if st.sidebar.button("Logout"):
        from auth.login import logout_user
        logout_user()
        st.rerun()

if __name__ == "__main__":
    main()
