# scoring.py
from typing import List, Dict
from models.analyzer import SentimentAnalyzer

def score_phrases_in_batches(all_phrases_text: List[str], analyzer: SentimentAnalyzer, batch_size: int) -> List[Dict[str, float]]:
    """
    Score phrases in batches for efficiency.
    """
    print(f"Analyzing sentiment for {len(all_phrases_text)} phrases in batches...")
    all_phrases = []
    for i in range(0, len(all_phrases_text), batch_size):
        batch_end = min(i + batch_size, len(all_phrases_text))
        batch_phrases = all_phrases_text[i:batch_end]
        batch_scores = [analyzer.score(phrase) for phrase in batch_phrases]
        for phrase, score in zip(batch_phrases, batch_scores):
            all_phrases.append({"text": phrase, "score": score})
        if len(all_phrases_text) > 500:
            print(f"Processed {batch_end}/{len(all_phrases_text)} phrases...")
    return all_phrases
