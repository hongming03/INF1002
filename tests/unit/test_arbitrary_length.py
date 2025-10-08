import pytest
from src.analysis.segment_finder import find_variable_length_segments

def test_normal_case():
    """
    Normal case: mixture of positive and negative scores.
    Should find correct most positive and most negative segments.
    """
    phrases = [
        {"text": "I love cats", "score": 3},
        {"text": "They are annoying sometimes", "score": -2},
        {"text": "But overall they are great", "score": 4},
        {"text": "I feed them daily", "score": 1}
    ]
    result = find_variable_length_segments(phrases)
    assert result["most_positive_segment"]["text"] == "I love cats. They are annoying sometimes. But overall they are great. I feed them daily" or result["most_positive_segment"]["score"] > 0
    assert result["most_negative_segment"]["score"] < 0

def test_all_positive_scores():
    """
    All positive scores → most positive = entire array,
    most negative = single phrase with smallest score.
    """
    phrases = [
        {"text": "Good", "score": 1},
        {"text": "Better", "score": 2},
        {"text": "Best", "score": 3}
    ]
    result = find_variable_length_segments(phrases)
    assert result["most_positive_segment"]["score"] == 6
    assert result["most_negative_segment"]["score"] == 1

def test_all_negative_scores():
    """
    All negative scores → most negative = entire array,
    most positive = single phrase with largest (least negative) score.
    """
    phrases = [
        {"text": "Bad", "score": -1},
        {"text": "Worse", "score": -3},
        {"text": "Worst", "score": -2}
    ]
    result = find_variable_length_segments(phrases)
    assert result["most_negative_segment"]["score"] == -6
    assert result["most_positive_segment"]["score"] == -1

def test_empty_list():
    """
    Empty input → both segments None.
    """
    result = find_variable_length_segments([])
    assert result["most_positive_segment"] is None
    assert result["most_negative_segment"] is None

def test_single_phrase():
    """
    Single phrase → both segments are the same phrase.
    """
    phrases = [{"text": "Neutral", "score": 0}]
    result = find_variable_length_segments(phrases)
    assert result["most_positive_segment"]["score"] == 0
    assert result["most_negative_segment"]["score"] == 0
    assert result["most_positive_segment"]["text"] == "Neutral"
    assert result["most_negative_segment"]["text"] == "Neutral"
