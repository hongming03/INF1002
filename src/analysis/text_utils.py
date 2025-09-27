# text_utils.py
import re
from typing import List, Dict

def split_texts_into_phrases(texts: List[str], max_words_per_segment: int) -> List[str]:
    """
    Split all texts into phrases based on punctuation and word count.
    """
    all_phrases_text = []
    for text in texts:
        phrases = [s.strip() for s in re.split(r'[,\;—:]', text) if s.strip()]
        split_phrases = []
        for phrase in phrases:
            words = phrase.split()
            if len(words) > max_words_per_segment:
                for i in range(0, len(words), max_words_per_segment):
                    split_phrases.append(" ".join(words[i:i+max_words_per_segment]))
            else:
                split_phrases.append(phrase)
        all_phrases_text.extend(split_phrases)
    return all_phrases_text

def create_sliding_window_segments(all_phrases: List[Dict[str, float]], window_size: int) -> List[Dict[str, float]]:
    """
    Create sliding window segments from scored phrases.
    """
    segments = []
    for i in range(len(all_phrases) - window_size + 1):
        segment = all_phrases[i:i + window_size]
        segment_text = ". ".join([s["text"] for s in segment]) + "."
        segment_score = sum([s["score"] for s in segment])
        segments.append({"text": segment_text, "score": segment_score})
    return segments
