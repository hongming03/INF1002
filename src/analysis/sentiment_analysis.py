# sentiment_analysis.py
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional
from models.analyzer import SentimentAnalyzer
from analysis.text_utils import split_texts_into_phrases, create_sliding_window_segments
from analysis.scoring import score_phrases_in_batches
from analysis.segment_finder import find_variable_length_segments

def analyze_sentences(
    texts: List[str], 
    analyzer: SentimentAnalyzer, 
    window_size: int = 1,
    max_words_per_segment: int = 20,
    batch_size: int = 100
) -> Dict[str, Optional[Dict[str, float]]]:
    """
    Run sentiment analysis on a list of texts and return key insights.
    This looks for:
      - The single most positive and negative phrases
      - Sliding window segments of phrases
      - Variable-length segments with extreme sentiment
    """

    # Step 1: Break all texts into smaller phrases so scoring is easier
    all_phrases_text = split_texts_into_phrases(texts, max_words_per_segment)

    # If no phrases are returned, just return None for all results
    if not all_phrases_text:
        return {
            "most_positive": None,
            "most_negative": None,
            "most_positive_segment": None,
            "most_negative_segment": None,
            "most_positive_variable_segment": None,
            "most_negative_variable_segment": None
        }

    # Step 2: Score each phrase using the sentiment analyzer, process in batches for efficiency
    all_phrases = score_phrases_in_batches(all_phrases_text, analyzer, batch_size)

    # Step 3: Identify the single most positive and most negative phrases
    def get_score(item):
        return item["score"]  # helper function to access the score key

    most_positive = max(all_phrases, key=get_score)
    most_negative = min(all_phrases, key=get_score)

    # Step 4: Create sliding window segments to capture context across multiple phrases
    segments = create_sliding_window_segments(all_phrases, window_size)
    most_positive_segment = max(segments, key=get_score, default=None)
    most_negative_segment = min(segments, key=get_score, default=None)

    # Step 5: Find variable-length segments that have the strongest sentiment
    variable_segments = find_variable_length_segments(all_phrases)

    # Step 6: Return all the key insights in one clean dictionary
    return {
        "most_positive": most_positive,
        "most_negative": most_negative,
        "most_positive_segment": most_positive_segment,
        "most_negative_segment": most_negative_segment,
        "most_positive_variable_segment": variable_segments["most_positive_segment"],
        "most_negative_variable_segment": variable_segments["most_negative_segment"]
    }


def analyze_by_fullstop(text: str):
    """
    Sentence-level scoring using full stops.
    """
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
