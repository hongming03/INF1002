# text_utils.py
import re
from typing import List, Dict

def split_texts_into_phrases(texts: List[str], max_words_per_segment: int) -> List[str]:
    """
    Break each text into smaller phrases.
    - Splits on common punctuation like commas, semicolons, dashes, and colons.
    - Further splits phrases if they have more words than max_words_per_segment.
    """
    all_phrases_text = []

    # Process each text individually
    for text in texts:
        # First, split text by punctuation and remove empty phrases
        phrases = [s.strip() for s in re.split(r'[,\;—:]', text) if s.strip()]
        split_phrases = []

        # Further split phrases that are too long
        for phrase in phrases:
            words = phrase.split()
            if len(words) > max_words_per_segment:
                # Break long phrases into smaller segments of max_words_per_segment words
                for i in range(0, len(words), max_words_per_segment):
                    split_phrases.append(" ".join(words[i:i+max_words_per_segment]))
            else:
                split_phrases.append(phrase)

        # Add all split phrases to the final list
        all_phrases_text.extend(split_phrases)

    return all_phrases_text


def create_sliding_window_segments(all_phrases: List[Dict[str, float]], window_size: int) -> List[Dict[str, float]]:
    """
    Combine consecutive phrases into sliding window segments.
    - Each segment contains 'window_size' phrases.
    - The segment's score is the sum of all phrase scores.
    - The segment's text joins all phrase texts with periods.
    Raises ValueError if window_size <= 0 or window_size > len(all_phrases).
    """
    if window_size <= 0:
        raise ValueError("window_size must be a positive integer.")
    if window_size > len(all_phrases):
        raise ValueError("window_size cannot be greater than the number of phrases.")

    segments = []

    # Slide a window across all phrases
    for i in range(len(all_phrases) - window_size + 1):
        segment = all_phrases[i:i + window_size]

        # Join the texts and sum the scores
        segment_text = ". ".join([s["text"] for s in segment]) + "."
        segment_score = sum([s["score"] for s in segment])

        # Store the segment as a dictionary
        segments.append({"text": segment_text, "score": segment_score})

    return segments