# analysis/segmentation.py
import os
import nltk
from nltk.corpus import words
from functools import lru_cache
from typing import List, Set, Dict
from models.analyzer import SentimentAnalyzer

# Make sure NLTK words are available
try:
    _ = words.words()
except LookupError:
    nltk.download("words")

# -------------------------------
# Dictionary helpers
# -------------------------------
@lru_cache(maxsize=1)
def get_english_dictionary() -> Set[str]:
    return set(w.lower() for w in words.words())

def load_wordlist(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

def get_extended_dictionary() -> Set[str]:
    # Merge English words + crypto_terms.txt + article_dict.txt
    base = get_english_dictionary()
    crypto_terms = load_wordlist("data/crypto_terms.txt")
    article_terms = load_wordlist("data/article_dict.txt")
    return base | crypto_terms | article_terms

# -------------------------------
# Clean text before segmentation
# -------------------------------
def clean_text_for_segmentation(text: str) -> str:
    analyzer = SentimentAnalyzer()
    tokens = analyzer._tokenize(text)  # lowercase + regex clean
    return "".join(tokens)  # glue tokens back together

# -------------------------------
# Segmentation core
# -------------------------------
def segment_text(text: str, dictionary: Set[str] = None) -> List[str]:
    """Return one valid segmentation using DP"""
    if dictionary is None:
        dictionary = get_extended_dictionary()

    n = len(text)
    dp = [None] * (n + 1)
    dp[0] = []

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] is not None and text[j:i] in dictionary:
                dp[i] = dp[j] + [text[j:i]]
                break
    return dp[n] if dp[n] else []

def all_segmentations(text: str, dictionary: Set[str] = None) -> List[List[str]]:
    """Return all possible segmentations (DFS + memo)"""
    if dictionary is None:
        dictionary = get_extended_dictionary()

    memo = {}
    def dfs(idx):
        if idx == len(text): return [[]]
        if idx in memo: return memo[idx]
        results = []
        for end in range(idx+1, len(text)+1):
            word = text[idx:end]
            if word in dictionary:
                for seg in dfs(end):
                    results.append([word] + seg)
        memo[idx] = results
        return results
    return dfs(0)

# -------------------------------
# Segmentation + Sentiment
# -------------------------------
def analyze_segmented_text(text: str, dictionary: Set[str] = None) -> Dict:
    if dictionary is None:
        dictionary = get_extended_dictionary()

    cleaned = clean_text_for_segmentation(text)
    one_seg = segment_text(cleaned, dictionary)

    if not one_seg:
        return {"original": text, "segmented": None, "score": 0}

    segmented_text = " ".join(one_seg)
    analyzer = SentimentAnalyzer()
    score = analyzer.score(segmented_text)

    return {
        "original": text,
        "segmented": segmented_text,
        "score": score
    }
