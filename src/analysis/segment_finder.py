# segment_finder.py
from typing import List, Dict

def find_variable_length_segments(phrases_with_scores: List[Dict[str, float]]) -> Dict[str, Dict]:
    """
    Find most positive/negative segments of arbitrary length using Kadane's algorithm.
    """
    if not phrases_with_scores:
        return {"most_positive_segment": None, "most_negative_segment": None}

    scores = [p["score"] for p in phrases_with_scores]

    # Positive segment
    max_sum = float('-inf')
    current_sum = 0
    start = end = temp_start = 0
    for i in range(len(scores)):
        current_sum += scores[i]
        if current_sum > max_sum:
            max_sum = current_sum
            start, end = temp_start, i
        if current_sum < 0:
            current_sum = 0
            temp_start = i + 1

    # Negative segment
    min_sum = float('inf')
    current_sum = 0
    min_start = min_end = temp_start = 0
    for i in range(len(scores)):
        current_sum += scores[i]
        if current_sum < min_sum:
            min_sum = current_sum
            min_start, min_end = temp_start, i
        if current_sum > 0:
            current_sum = 0
            temp_start = i + 1

    pos_phrases = phrases_with_scores[start:end+1]
    neg_phrases = phrases_with_scores[min_start:min_end+1]

    return {
        "most_positive_segment": {
            "text": ". ".join([p["text"] for p in pos_phrases]),
            "score": max_sum,
            "phrase_indices": list(range(start, end+1))
        },
        "most_negative_segment": {
            "text": ". ".join([p["text"] for p in neg_phrases]),
            "score": min_sum,
            "phrase_indices": list(range(min_start, min_end+1))
        }
    }
