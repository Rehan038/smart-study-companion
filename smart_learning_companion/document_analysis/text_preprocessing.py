import re, string, nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords as sw

def _ensure_nltk_data():
    for r in ["punkt", "stopwords"]:
        try:
            nltk.data.find(f"tokenizers/{r}" if r=="punkt" else f"corpora/{r}")
        except:
            nltk.download(r, quiet=True)

_ensure_nltk_data()

def clean_text(text):
    """Lowercases and removes punctuation."""
    if not text: return ""
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", text).strip()

def tokenize_text(text):
    """Word tokenization."""
    return word_tokenize(text) if text else []

def remove_stopwords(tokens):
    """Removes standard English stopwords."""
    stop = set(sw.words("english"))
    return [t for t in tokens if t not in stop and len(t) > 1]
