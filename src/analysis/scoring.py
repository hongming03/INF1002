# scoring.py
from typing import List, Dict
from models.analyzer import SentimentAnalyzer

def score_phrases_in_batches(
    all_phrases_text: List[str], 
    analyzer: SentimentAnalyzer, 
    batch_size: int
) -> List[Dict[str, float]]:
    """
    Score a list of phrases in batches for efficiency.
    Returns a list of dictionaries with each phrase and its sentiment score.
    """

    # This will store the scored phrases
    all_phrases = []

    # Process phrases in chunks of size `batch_size`
    for i in range(0, len(all_phrases_text), batch_size):
        # Determine the end of the current batch
        batch_end = min(i + batch_size, len(all_phrases_text))
        # Get the phrases for this batch
        batch_phrases = all_phrases_text[i:batch_end]

        # Score each phrase using the sentiment analyzer
        batch_scores = [analyzer.score(phrase) for phrase in batch_phrases]

        # Combine phrases and their scores into dictionaries
        for phrase, score in zip(batch_phrases, batch_scores):
            all_phrases.append({"text": phrase, "score": score})

        # Optional: if you want to provide progress info for very large inputs, 
        # you could use logging instead of print

    # Return all phrases with their sentiment scores
    return all_phrases
