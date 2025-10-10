# segment_finder.py
from typing import List, Dict

def find_variable_length_segments(phrases_with_scores: List[Dict[str, float]]) -> Dict[str, Dict]:
    """
    Find most positive/negative segments of arbitrary length using Kadane's algorithm.
    """
    # Return empty result if no phrases are provided
    if not phrases_with_scores:
        return {"most_positive_segment": None, "most_negative_segment": None}

    # Extract all the sentiment scores from the input
    scores = [p["score"] for p in phrases_with_scores]

    # --- Find most positive segment (maximum subarray) ---
    max_sum = float('-inf')   # Best total score found so far
    current_sum = 0           # Current running total
    start = end = temp_start = 0  # Track start and end of the best segment

    for i in range(len(scores)):
        current_sum += scores[i]  # Add current score to the running total

        # If this running total is better than what we've seen, update the best range
        if current_sum > max_sum:
            max_sum = current_sum
            start, end = temp_start, i

        # If total drops below zero, reset and start a new segment
        if current_sum < 0:
            current_sum = 0
            temp_start = i + 1

    # --- Find most negative segment (minimum subarray) ---
    min_sum = float('inf')    # Lowest total score found so far
    current_sum = 0
    min_start = min_end = temp_start = 0

    for i in range(len(scores)):
        current_sum += scores[i]  # Keep adding to running total

        # If this total is the smallest so far, mark this range as the worst segment
        if current_sum < min_sum:
            min_sum = current_sum
            min_start, min_end = temp_start, i

        # If total becomes positive, reset since negative segment ended
        if current_sum > 0:
            current_sum = 0
            temp_start = i + 1

    # Get the actual phrases for both segments
    pos_phrases = phrases_with_scores[start:end+1]
    neg_phrases = phrases_with_scores[min_start:min_end+1]

    # Return both segments with their texts, scores, and index ranges
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
