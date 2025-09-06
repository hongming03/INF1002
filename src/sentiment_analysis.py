import re
from typing import List, Dict, Optional
from analyzer import SentimentAnalyzer

 # Split business logic with the afinn library

def analyze_sentences(texts: List[str], analyzer: SentimentAnalyzer, window_size: int = 3) -> Dict[str, Optional[Dict[str, float]]]:
    """
    Splits texts into sentences, scores them, and returns most positive/negative sentences and segments.
    """
    # Split and score sentences
    all_sentences = []
    for text in texts:
        sentences = [s.strip() for s in re.split(r'\.\s*', text) if s.strip()]
        for sentence in sentences:
            score = analyzer.score(sentence)
            all_sentences.append({"text": sentence, "score": score})

    # Find extremes
    most_positive = max(all_sentences, key=lambda x: x["score"], default=None)
    most_negative = min(all_sentences, key=lambda x: x["score"], default=None)

    # Sliding window segments
    segments = []
    for i in range(len(all_sentences) - window_size + 1):
        segment = all_sentences[i:i + window_size]
        segment_text = ". ".join([s["text"] for s in segment]) + "."
        segment_score = sum([s["score"] for s in segment])
        segments.append({"text": segment_text, "score": segment_score})

    most_positive_segment = max(segments, key=lambda x: x["score"], default=None)
    most_negative_segment = min(segments, key=lambda x: x["score"], default=None)

    return {
        "most_positive": most_positive,
        "most_negative": most_negative,
        "most_positive_segment": most_positive_segment,
        "most_negative_segment": most_negative_segment
    }
