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
    Main sentiment analysis pipeline.
    """
    print("Breaking texts into phrases...")
    all_phrases_text = split_texts_into_phrases(texts, max_words_per_segment)
    if not all_phrases_text:
        return {
            "most_positive": None,
            "most_negative": None,
            "most_positive_segment": None,
            "most_negative_segment": None,
            "most_positive_variable_segment": None,
            "most_negative_variable_segment": None
        }

    all_phrases = score_phrases_in_batches(all_phrases_text, analyzer, batch_size)

    print("Finding most extreme phrases...")
    most_positive = max(all_phrases, key=lambda x: x["score"])
    most_negative = min(all_phrases, key=lambda x: x["score"])

    print("Creating sliding window segments...")
    segments = create_sliding_window_segments(all_phrases, window_size)
    most_positive_segment = max(segments, key=lambda x: x["score"], default=None)
    most_negative_segment = min(segments, key=lambda x: x["score"], default=None)

    print("Finding variable-length segments...")
    variable_segments = find_variable_length_segments(all_phrases)

    print("Analysis complete!")
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
