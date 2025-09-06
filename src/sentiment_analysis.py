import re
from typing import List, Dict, Optional
from analyzer import SentimentAnalyzer

def analyze_sentences(
    texts: List[str], 
    analyzer: SentimentAnalyzer, 
    window_size: int = 1,   # Default to 1 for short headlines
    max_words_per_segment: int = 20  # Optional fallback for very long phrases
) -> Dict[str, Optional[Dict[str, float]]]:
    """
    Splits texts into phrases (based on punctuation), scores them, 
    and returns most positive/negative phrases and sliding window segments.
    """
    # Split and score phrases
    all_phrases = []
    for text in texts:
        # Split by punctuation marks often used in headlines
        phrases = [s.strip() for s in re.split(r'[,\;—:]', text) if s.strip()]
        
        # Optional: split long phrases by word count
        split_phrases = []
        for phrase in phrases:
            words = phrase.split()
            if len(words) > max_words_per_segment:
                # Split into smaller chunks
                for i in range(0, len(words), max_words_per_segment):
                    split_phrases.append(" ".join(words[i:i+max_words_per_segment]))
            else:
                split_phrases.append(phrase)
        
        # Score each phrase
        for phrase in split_phrases:
            score = analyzer.score(phrase)
            all_phrases.append({"text": phrase, "score": score})

    if not all_phrases:
        return {
            "most_positive": None,
            "most_negative": None,
            "most_positive_segment": None,
            "most_negative_segment": None
        }

    # Find extreme phrases
    most_positive = max(all_phrases, key=lambda x: x["score"])
    most_negative = min(all_phrases, key=lambda x: x["score"])

    # Sliding window segments
    segments = []
    for i in range(len(all_phrases) - window_size + 1):
        segment = all_phrases[i:i + window_size]
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
