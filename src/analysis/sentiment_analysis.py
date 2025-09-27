# sentiment_analysis.py
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional
from models.analyzer import SentimentAnalyzer
from analysis.text_utils import split_texts_into_phrases, create_sliding_window_segments
from analysis.scoring import score_phrases_in_batches
from analysis.segment_finder import find_variable_length_segments
from reporting.analytics import get_sentiment_summary

# -------------------------------
# Utility: Sentence-level scoring
# -------------------------------
def score_sentences_by_fullstop(text: str) -> pd.DataFrame:
    if not text or not text.strip():
        return pd.DataFrame()

    sentences = [s.strip() for s in text.split(".") if s.strip()]
    analyzer = SentimentAnalyzer()
    rows = [{
        "text": s,
        "SentimentScore": analyzer.score(s),
        "date": datetime.today().strftime("%Y-%m-%d")
    } for s in sentences]

    return pd.DataFrame(rows)

# -------------------------------
# Utility: Phrase-level scoring
# -------------------------------
def score_phrases(texts: List[str], analyzer: SentimentAnalyzer, max_words: int = 20, batch_size: int = 100) -> List[Dict]:
    phrases = split_texts_into_phrases(texts, max_words)
    if not phrases:
        return []
    return score_phrases_in_batches(phrases, analyzer, batch_size)

# -------------------------------
# Main Analysis Engine
# -------------------------------
def run_full_sentiment_analysis(
    texts: List[str],
    analyzer: SentimentAnalyzer,
    window_size: int = 1,
    max_words_per_segment: int = 20,
    batch_size: int = 100
) -> Dict[str, Optional[Dict]]:
    phrases = score_phrases(texts, analyzer, max_words_per_segment, batch_size)
    if not phrases:
        return {
            "most_positive": None,
            "most_negative": None,
            "most_positive_segment": None,
            "most_negative_segment": None,
            "most_positive_variable_segment": None,
            "most_negative_variable_segment": None
        }

    def get_score(item): return item["score"]

    most_positive = max(phrases, key=get_score)
    most_negative = min(phrases, key=get_score)

    segments = create_sliding_window_segments(phrases, window_size)
    most_positive_segment = max(segments, key=get_score, default=None)
    most_negative_segment = min(segments, key=get_score, default=None)

    variable_segments = find_variable_length_segments(phrases)

    return {
        "most_positive": most_positive,
        "most_negative": most_negative,
        "most_positive_segment": most_positive_segment,
        "most_negative_segment": most_negative_segment,
        "most_positive_variable_segment": variable_segments["most_positive_segment"],
        "most_negative_variable_segment": variable_segments["most_negative_segment"]
    }

# -------------------------------
# Wrapper: Unified Analysis
# -------------------------------
def analyze_text(text: str, mode: str = "full") -> Dict:
    analyzer = SentimentAnalyzer()
    if mode == "sentence":
        df = score_sentences_by_fullstop(text)
        avg_score = df["SentimentScore"].mean() if not df.empty else 0
        summary = get_sentiment_summary(df, avg_score)
        return {"summary": summary, "raw": df}
    else:
        return run_full_sentiment_analysis([text], analyzer)
