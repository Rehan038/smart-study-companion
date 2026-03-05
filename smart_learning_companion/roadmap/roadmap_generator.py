import re
import string
import nltk
import wikipedia
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords as sw
from database.db import save_roadmap

# ── Step 1: NLTK Data Check ──────────────────────────────────────────────────
def _ensure_nltk_data():
    for r in ["punkt", "punkt_tab", "stopwords"]:
        try:
            if r == "punkt":
                nltk.data.find("tokenizers/punkt")
            elif r == "punkt_tab":
                nltk.data.find("tokenizers/punkt_tab")
            else:
                nltk.data.find("corpora/stopwords")
        except:
            nltk.download(r, quiet=True)

_ensure_nltk_data()

# ── Knowledge Base (Foundational & Reliable) ──────────────────────────────────
KNOWLEDGE_BASE = {
    "machine learning": ["Linear Algebra", "Calculus", "Probability", "Supervised Learning", "Unsupervised Learning", "Deep Learning", "Model Deployment"],
    "python": ["Syntax & Variables", "Data Structures", "Functions & Modules", "Exception Handling", "File I/O", "OOP Principles", "Web Frameworks"],
    "data science": ["Data Exploration", "Statistical Analysis", "Data Cleaning", "Data Visualization", "Predictive Modeling", "Big Data", "Case Study"],
    "web development": ["HTML5/CSS3", "JavaScript Basics", "Responsive Design", "Frontend Frameworks", "Backend APIs", "Database Integration", "Deployment"],
    "artificial intelligence": ["History & Logic", "Search Algorithms", "Knowledge Representation", "NLP Foundations", "Computer Vision", "Robotics", "Ethics in AI"],
    "sql": ["Database Basics", "SELECT & Filtering", "Joins & Unions", "Aggregations", "Subqueries", "Indexing & Optimization", "Schema Design"],
    "java": ["JVM Architecture", "Object-Oriented Programming", "Collections Framework", "Exception Handling", "Multithreading", "Spring Boot", "Unit Testing"],
    "react": ["JSX & Elements", "Components & Props", "State Management (Hooks)", "Effect & Lifecycle", "Routing", "API Integration", "Performance Optimization"]
}

# ── Enhanced Ranking Heuristic ───────────────────────────────────────────────
def rank_concept(c):
    """Assigns priority for learning order."""
    l = c.lower()
    # Priority 0: Foundations
    if any(x in l for x in ["intro", "basic", "foundation", "history", "principle", "syntax", "background"]): return 0
    # Priority 10: Advanced/Deployment
    if any(x in l for x in ["advanced", "expert", "optimization", "neural", "deployment", "expert", "security", "infrastructure"]): return 10
    # Priority 5: Core Techniques
    if any(x in l for x in ["algorithm", "method", "logic", "framework", "library", "implementation", "data", "system"]): return 5
    return 7

def estimate_difficulty(concept):
    """Heuristic for level and study hours."""
    l = concept.lower()
    if any(x in l for x in ["intro", "basic", "history", "what is", "syntax"]): return "Beginner", 4
    if any(x in l for x in ["advanc", "deep", "neural", "optimization", "expert"]): return "Advanced", 10
    if any(x in l for x in ["project", "application", "case study", "final"]): return "Project", 12
    return "Intermediate", 7

# ── Core Roadmap Logic v3.1 ──────────────────────────────────────────────────
def generate_roadmap(topic, pdf_keywords=None):
    if not topic: return _fallback("Learning Path")
    
    query = topic.strip()
    concepts = []
    
    # 1. Knowledge Base Match (Highest Precision)
    if query.lower() in KNOWLEDGE_BASE:
        concepts = list(KNOWLEDGE_BASE[query.lower()])
    
    # 2. Wikipedia Deep Extraction (Accuracy Focused)
    if not concepts:
        try:
            # Multi-stage searching to handle disambiguation and noise
            search_results = wikipedia.search(query, results=5)
            if search_results:
                best_page = None
                for res in search_results:
                    try:
                        # Fetch page without auto-suggest for precision
                        page = wikipedia.page(res, auto_suggest=False)
                        # Avoid 'List of' or vague pages
                        if "list of" in page.title.lower() or len(page.content) < 500: continue
                        
                        # Extract H2 headings
                        headings = re.findall(r"== (.*?) ==", page.content)
                        # Strict Blacklist for generic/noise sections
                        blacklist = ["references", "external links", "further reading", "see also", "notes", 
                                     "bibliography", "history", "description", "etymology", "classification", 
                                     "terminology", "development", "origin", "background", "summary", "names", 
                                     "gallery", "overview", "packet", "documents", "sections"]
                        
                        valid = []
                        for h in headings:
                            h_clean = h.strip()
                            # Quality filter: length, no numbers-only, not in blacklist
                            if (h_clean.lower() not in blacklist and len(h_clean) > 3 
                                and not h_clean.endswith(":") and not any(char.isdigit() for char in h_clean[:1])):
                                valid.append(h_clean)
                        
                        if len(valid) >= 4:
                            concepts = valid[:8]
                            break # Success with headings
                        else:
                            # Fallback: Scrape Nouns from Summary for keywords
                            summary = page.summary[:1000]
                            tokens = word_tokenize(summary)
                            # POS tagging like approach (filtering for significant concepts)
                            stop_words = set(sw.words('english'))
                            kw_set = []
                            for w in tokens:
                                if (w.lower() not in stop_words and len(w) > 4 and 
                                    w[0].isupper() and w.isalpha()):
                                    kw_set.append(w)
                            
                            unique_kws = sorted(list(set(kw_set)))
                            if len(unique_kws) >= 5:
                                concepts = unique_kws[:8]
                                break
                    except: continue
        except: pass

    # 3. PDF Semantic Integration (Smart Weaving)
    if pdf_keywords:
        # Filter for concrete nouns, ignore generic analyzer noise and common filler words
        ignore_analyst = ["document", "analysis", "summary", "keywords", "concept", "learning", "packet", "study", "report", "overview", "circuit", "switching"]
        valid_pdf = [k for k in pdf_keywords if len(k) > 5 and k.lower() not in ignore_analyst]
        
        # 🧪 Semantic Overlap Guard 🧪
        # Only weave keywords that have some relevance to the topic's context.
        # We check if the keyword or the topic share any common technical prefixes or substrings.
        topic_words = set(query.lower().split())
        
        to_weave = []
        for kw in valid_pdf:
            kw_l = kw.lower()
            # Simple heuristic: if the keyword appears in the Knowledge Base or Wikipedia headings, it's relevant.
            # Otherwise, we check for technical suffixes or common domain overlaps.
            is_relevant = False
            if any(w in kw_l for w in topic_words) or any(topic_word in kw_l for topic_word in topic_words):
                is_relevant = True
            
            # Additional check: Does it look like a technical 'concept'? (e.g. ends in -ing, -ion, -ism, -ity)
            if any(kw_l.endswith(s) for s in ["ing", "ion", "ism", "ity", "ics", "logy", "ware", "data"]):
                is_relevant = True
            
            if is_relevant: to_weave.append(kw)

        # Weave top 2 relevant keywords into appropriate slots
        for i, kw in enumerate(to_weave[:2]):
            if kw.lower() not in [c.lower() for c in concepts]:
                pos = 3 if i == 0 else 6 # Middle/Advanced sections
                concepts.insert(min(pos, len(concepts)), kw)

    # 4. Fallback (If logic yields 'trash' or empty)
    if len(concepts) < 3:
        return _fallback(query)

    # 5. Logical Flow Optimization
    unique_list = []
    seen = set()
    for c in concepts:
        if c.lower() not in seen:
            unique_list.append(c)
            seen.add(c.lower())
    
    # Sort by learning priority
    final_concepts = sorted(unique_list, key=rank_concept)

    # 6. Structuring
    roadmap_list = []
    for i, c in enumerate(final_concepts[:10]):
        lvl, hrs = estimate_difficulty(c)
        roadmap_list.append({
            "week": i + 1,
            "concept": c,
            "level": lvl,
            "hours": hrs
        })

    # Prepare Display Text
    text_out = f"Expert Roadmap: {query.upper()}\n" + "="*(len(query)+16) + "\n"
    for item in roadmap_list:
        text_out += f"Week {item['week']}: {item['concept']} [{item['level']} | ~{item['hours']} hrs]\n"
        
    save_roadmap(query, text_out)
    G = build_learning_graph(roadmap_list)
    return roadmap_list, G

def _fallback(topic):
    core = ["Fundamentals & Core Theory", "Architectural Overview", "Key Methodologies & Tools", 
            "Intermediate Implementation", "Advanced Optimization Techniques", "Enterprise Integration & Deployment", "Hands-on Project Portfolio"]
    roadmap_list = []
    for i, c in enumerate(core):
        lvl, hrs = estimate_difficulty(c)
        roadmap_list.append({"week": i+1, "concept": f"{topic} {c}", "level": lvl, "hours": hrs})
    G = build_learning_graph(roadmap_list)
    return roadmap_list, G

# ── Visual Helpers ──────────────────────────────────────────────────────────
def build_learning_graph(roadmap):
    G = nx.DiGraph()
    concepts = [item['concept'] for item in roadmap]
    for i, concept in enumerate(concepts):
        G.add_node(concept)
        if i > 0: G.add_edge(concepts[i-1], concept)
    return G

def get_graph_fig(G):
    if not G.nodes(): return go.Figure()
    pos = nx.spring_layout(G, k=1.2, iterations=50)
    
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=2, color='#38bdf8'), hoverinfo='none', mode='lines')

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', text=node_text,
        textposition="top center",
        marker=dict(showscale=False, color='#0ea5e9', size=30, line=dict(width=2, color='#f1f5f9')),
        hoverinfo='text',
        textfont=dict(color='#f1f5f9', size=11)
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False, hovermode='closest',
                    margin=dict(b=0, l=0, r=0, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    template="plotly_dark"
                ))
    return fig
