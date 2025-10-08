import sys
import os

# Add the src folder to the path so 'models' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from src.analysis.scoring import score_phrases_in_batches

# Mock SentimentAnalyzer class to simulate scoring behavior
class MockAnalyzer:
    def score(self, phrase):
        # Simple mock scoring function:
        # Returns number of characters divided by 10 for consistency
        return len(phrase) / 10.0


def test_normal_batch_processing():
    """
    Test normal case with multiple batches.
    Ensures that all phrases are scored correctly and order is preserved.
    """
    analyzer = MockAnalyzer()
    phrases = ["happy", "sad", "excited"]
    result = score_phrases_in_batches(phrases, analyzer, batch_size=2)

    expected = [
        {"text": "happy", "score": 0.5},
        {"text": "sad", "score": 0.3},
        {"text": "excited", "score": 0.7},
    ]
    assert result == expected


def test_empty_input():
    """
    Edge Case 1: Empty list.
    Should return an empty list.
    """
    analyzer = MockAnalyzer()
    result = score_phrases_in_batches([], analyzer, batch_size=3)
    assert result == []


def test_batch_size_larger_than_list():
    """
    Edge Case 2: Batch size greater than list length.
    Should process entire list in one batch.
    """
    analyzer = MockAnalyzer()
    phrases = ["joy", "anger"]
    result = score_phrases_in_batches(phrases, analyzer, batch_size=10)
    expected = [
        {"text": "joy", "score": 0.3},
        {"text": "anger", "score": 0.5},
    ]
    assert result == expected


def test_single_phrase():
    """
    Edge Case 3: Only one phrase in list.
    Should handle single-element input correctly.
    """
    analyzer = MockAnalyzer()
    result = score_phrases_in_batches(["neutral"], analyzer, batch_size=1)
    assert result == [{"text": "neutral", "score": 0.7}]

