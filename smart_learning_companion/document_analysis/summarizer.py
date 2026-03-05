from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords as sw

def generate_summary(text, sentence_count=5):
    """Extractive summarization using sentence scoring."""
    if not text or not text.strip(): return ""
    sents = sent_tokenize(text)
    if len(sents) <= sentence_count: return text.strip()
    
    stop = set(sw.words("english"))
    words = [w.lower() for w in word_tokenize(text) if w.isalpha() and w.lower() not in stop]
    if not words: return " ".join(sents[:sentence_count])
    
    freq = Counter(words)
    max_f = max(freq.values())
    w_freq = {w: c/max_f for w, c in freq.items()}
    
    scores = {}
    for s in sents:
        for w in word_tokenize(s.lower()):
            if w in w_freq: scores[s] = scores.get(s, 0) + w_freq[w]
            
    top = sorted(scores, key=scores.get, reverse=True)[:sentence_count]
    return " ".join([s for s in sents if s in top])
