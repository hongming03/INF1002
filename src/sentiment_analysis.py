# sentiment_analysis.py
import re
from typing import List, Dict, Optional
from analyzer import SentimentAnalyzer

def _split_texts_into_phrases(texts: List[str], max_words_per_segment: int) -> List[str]:
    """
    Split all texts into phrases based on punctuation and word count.
    """
    all_phrases_text = []
    
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
        
        # Add all phrases to our list (just text for now)
        all_phrases_text.extend(split_phrases)
    
    return all_phrases_text

def _score_phrases_in_batches(all_phrases_text: List[str], analyzer: SentimentAnalyzer, batch_size: int) -> List[Dict[str, float]]:
    """
    Score phrases in batches for efficiency.
    """
    print(f"Analyzing sentiment for {len(all_phrases_text)} phrases in batches...")
    all_phrases = []  # Will store {"text": phrase, "score": score}
    
    # Process phrases in batches to reduce function call overhead
    for i in range(0, len(all_phrases_text), batch_size):
        # Get a batch of phrases
        batch_end = min(i + batch_size, len(all_phrases_text))
        batch_phrases = all_phrases_text[i:batch_end]
        
        # Score all phrases in this batch
        batch_scores = []
        for phrase in batch_phrases:
            score = analyzer.score(phrase)
            batch_scores.append(score)
        
        # Combine text and scores for this batch
        for phrase, score in zip(batch_phrases, batch_scores):
            all_phrases.append({"text": phrase, "score": score})
        
        # Show progress for large datasets
        if len(all_phrases_text) > 500:
            print(f"Processed {batch_end}/{len(all_phrases_text)} phrases...")
    
    return all_phrases

def _create_sliding_window_segments(all_phrases: List[Dict[str, float]], window_size: int) -> List[Dict[str, float]]:
    """
    Create sliding window segments from scored phrases.
    """
    segments = []
    
    # Create overlapping windows of phrases
    for i in range(len(all_phrases) - window_size + 1):
        # Get a window of phrases
        segment = all_phrases[i:i + window_size]
        
        # Combine the phrases in this window into one text
        segment_text = ". ".join([s["text"] for s in segment]) + "."
        
        # Sum up the scores of all phrases in this window
        segment_score = sum([s["score"] for s in segment])
        
        segments.append({"text": segment_text, "score": segment_score})
    
    return segments

def analyze_sentences(
    texts: List[str], 
    analyzer: SentimentAnalyzer, 
    window_size: int = 1,   # Default to 1 for short headlines
    max_words_per_segment: int = 20,  # Optional fallback for very long phrases
    batch_size: int = 100  # Process this many phrases at once for efficiency
) -> Dict[str, Optional[Dict[str, float]]]:
    """
    Splits texts into phrases (based on punctuation), scores them, 
    and returns most positive/negative phrases and sliding window segments.
    """
    
    # Step 1: Split all texts into phrases first (no scoring yet)
    print("Breaking texts into phrases...")
    all_phrases_text = _split_texts_into_phrases(texts, max_words_per_segment)
    
    if not all_phrases_text:
        return {
            "most_positive": None,
            "most_negative": None,
            "most_positive_segment": None,
            "most_negative_segment": None
        }
    
    # Step 2: Score phrases in batches for efficiency
    all_phrases = _score_phrases_in_batches(all_phrases_text, analyzer, batch_size)
    
    # Step 3: Find extreme phrases (most positive/negative individual phrases)
    print("Finding most extreme phrases...")
    most_positive = max(all_phrases, key=lambda x: x["score"])
    most_negative = min(all_phrases, key=lambda x: x["score"])
    
    # Step 4: Create sliding window segments and find extreme segments
    print("Creating sliding window segments...")
    segments = _create_sliding_window_segments(all_phrases, window_size)
    
    # Find the most extreme segments (windows with highest/lowest combined scores)
    most_positive_segment = max(segments, key=lambda x: x["score"], default=None)
    most_negative_segment = min(segments, key=lambda x: x["score"], default=None)
    
    print("Analysis complete!")
    
    return {
        "most_positive": most_positive,           # Single phrase with highest score
        "most_negative": most_negative,           # Single phrase with lowest score
        "most_positive_segment": most_positive_segment,  # Window of phrases with highest combined score
        "most_negative_segment": most_negative_segment   # Window of phrases with lowest combined score
    }