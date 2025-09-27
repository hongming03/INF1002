# segment_finder.py
from typing import List, Dict

def find_variable_length_segments(phrases_with_scores: List[Dict[str, float]]) -> Dict[str, Dict]:
    """
    Find the most positive and most negative segments in a list of phrases.
    Uses Kadane's algorithm to handle segments of any length.
    """

    # If no phrases are provided, return None
    if not phrases_with_scores:
        return {"most_positive_segment": None, "most_negative_segment": None}

    # Extract the scores for easier processing
    scores = [p["score"] for p in phrases_with_scores]

    # -----------------------
    # Find the most positive segment
    # -----------------------
    max_sum = float('-inf')  # Start with the smallest possible number
    current_sum = 0
    start = end = temp_start = 0  # Track segment indices

    for i in range(len(scores)):
        current_sum += scores[i]  # Add score of the current phrase

        # Update max_sum if this segment is the largest so far
        if current_sum > max_sum:
            max_sum = current_sum
            start, end = temp_start, i  # Save the start and end of this segment

        # If the sum goes negative, reset it and start a new segment
        if current_sum < 0:
            current_sum = 0
            temp_start = i + 1

    # -----------------------
    # Find the most negative segment
    # -----------------------
    min_sum = float('inf')  # Start with the largest possible number
    current_sum = 0
    min_start = min_end = temp_start = 0

    for i in range(len(scores)):
        current_sum += scores[i]  # Add score of the current phrase

        # Update min_sum if this segment is the smallest so far
        if current_sum < min_sum:
            min_sum = current_sum
            min_start, min_end = temp_start, i

        # If the sum goes positive, reset it and start a new segment
        if current_sum > 0:
            current_sum = 0
            temp_start = i + 1

    # Collect phrases for each segment
    pos_phrases = phrases_with_scores[start:end+1]
    neg_phrases = phrases_with_scores[min_start:min_end+1]

    # Return results in a clear, easy-to-use format
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
