from collections import Counter
import nltk

def extract_keywords(tokens, top_n=10):
    """Return top N keywords by frequency, filtering for significant concepts."""
    if not tokens: return []
    
    # ── Technical Significance Filter ──
    # We prioritize words that look like proper nouns or technical concepts
    # Standard English words usually don't have capitals in tokens, but we check length and content
    ignore = ["document", "analysis", "summary", "keywords", "concept", "learning", "packet", "study", "report", "overview", "circuit", "switching", "section", "system", "using", "within", "across"]
    
    # Filtering for words > 4 chars and not in the noise list
    concepts = [t for t in tokens if len(t) > 5 and t.lower() not in ignore]
    
    return Counter(concepts).most_common(top_n)
