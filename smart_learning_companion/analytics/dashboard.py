import pandas as pd, plotly.express as px, streamlit as st, math
from pathlib import Path
from document_analysis.pdf_reader import extract_text_from_pdf
from document_analysis.text_preprocessing import clean_text, tokenize_text, remove_stopwords
from document_analysis.keyword_extraction import extract_keywords
from document_analysis.summarizer import generate_summary
from roadmap.roadmap_generator import generate_roadmap
from roadmap.feedback import show_feedback_page
from database.db import save_document

U_DIR = Path(__file__).parent.parent / "data" / "uploads"

def _nlp_stats(text, tokens, filtered):
    words = len(text.split())
    uniq = len(set(filtered))
    diversity = (uniq / words) if words > 0 else 0
    reading_time = math.ceil(words / 200)
    # Simulated readability: higher avg words per sentence = lower score
    sents = text.count('.') + text.count('?') + 1
    readability = max(0, min(100, 120 - (1.015 * (words/sents)) - (84.6 * (tokens.count('e')/words if words else 0))))
    return reading_time, diversity, readability

def _page_upload_pdf():
    st.header("📂 Document Center")
    f = st.file_uploader("Upload PDF", type=["pdf"])
    if f:
        U_DIR.mkdir(parents=True, exist_ok=True)
        p = U_DIR / f.name
        with open(p, "wb") as fh: fh.write(f.getbuffer())
        try:
            txt = extract_text_from_pdf(p)
            st.session_state["doc_text"], st.session_state["doc_filename"] = txt, f.name
            save_document(st.session_state["username"], f.name)
            st.success("Uploaded!")
        except Exception as e: st.error(str(e))

def _page_analyze_document():
    st.header("🔍 NLP Insights")
    if "doc_text" not in st.session_state: st.warning("Upload first"); return
    txt = st.session_state["doc_text"]
    cleaned = clean_text(txt)
    tokens = tokenize_text(cleaned)
    filtered = remove_stopwords(tokens)
    kw = extract_keywords(filtered, top_n=30)
    
    rt, div, read = _nlp_stats(txt, tokens, filtered)
    c1, c2, c3 = st.columns(3)
    c1.metric("Est. Reading Time", f"{rt} min")
    c2.metric("Lexical Diversity", f"{div:.2%}")
    c3.metric("Readability Score", f"{read:.1f}")
    
    if kw:
        st.subheader("Map of Content (Treemap)")
        df = pd.DataFrame(kw, columns=["Keyword", "Weight"])
        st.plotly_chart(px.treemap(df, path=["Keyword"], values="Weight", title="Topic Hierarchy", template="plotly_dark"), use_container_width=True)
        st.plotly_chart(px.bar(df.head(10), x="Weight", y="Keyword", orientation="h", title="Top Keywords", template="plotly_dark"), use_container_width=True)
    st.session_state["doc_keywords"] = kw

def _page_generate_summary():
    st.header("📝 Smart Summary")
    if "doc_text" not in st.session_state: st.warning("Upload first"); return
    c = st.slider("Sentences", 3, 15, 5)
    if st.button("Generate"): st.info(generate_summary(st.session_state["doc_text"], sentence_count=c))

def _page_generate_roadmap():
    st.header("🗺️ Dynamic Roadmap")
    t = st.text_input("Study Topic")
    if st.button("Generate") and t:
        rid, text = generate_roadmap(st.session_state["username"], t, st.session_state.get("doc_keywords"))
        st.session_state["last_roadmap_text"] = text
        st.success(f"Roadmap Created (ID: {rid})")
    if "last_roadmap_text" in st.session_state: st.text(st.session_state["last_roadmap_text"])

def show_student_dashboard():
    from auth.login import logout_user
    with st.sidebar:
        st.title("Student Portal")
        p = st.radio("Nav", ["📂 Upload", "🔍 NLP Analytics", "📝 Summary", "🗺️ Roadmap", "💬 Feedback"])
        if st.button("Logout"): logout_user(); st.rerun()
    if p == "📂 Upload": _page_upload_pdf()
    elif p == "🔍 NLP Analytics": _page_analyze_document()
    elif p == "📝 Summary": _page_generate_summary()
    elif p == "🗺️ Roadmap": _page_generate_roadmap()
    elif p == "💬 Feedback": show_feedback_page()
