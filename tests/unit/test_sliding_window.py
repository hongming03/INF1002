import pytest
from src.analysis.text_utils import create_sliding_window_segments

def test_normal_case():
    """Normal case: multiple phrases, window size 2."""
    phrases = [
        {"text": "I love cats", "score": 3},
        {"text": "They are cute", "score": 2},
        {"text": "I feed them daily", "score": 1}
    ]
    result = create_sliding_window_segments(phrases, window_size=2)
    expected = [
        {"text": "I love cats. They are cute.", "score": 5},
        {"text": "They are cute. I feed them daily.", "score": 3}
    ]
    assert result == expected

def test_window_size_one():
    """window_size = 1 → each phrase is its own segment."""
    phrases = [
        {"text": "Happy", "score": 1},
        {"text": "Sad", "score": -1}
    ]
    result = create_sliding_window_segments(phrases, window_size=1)
    expected = [
        {"text": "Happy.", "score": 1},
        {"text": "Sad.", "score": -1}
    ]
    assert result == expected

def test_window_size_equals_phrases():
    """window_size = total phrases → single segment with all phrases combined."""
    phrases = [
        {"text": "Good", "score": 1},
        {"text": "Bad", "score": -1}
    ]
    result = create_sliding_window_segments(phrases, window_size=2)
    expected = [{"text": "Good. Bad.", "score": 0}]
    assert result == expected

def test_window_size_zero_raises():
    """window_size <= 0 should raise ValueError."""
    phrases = [{"text": "Hello", "score": 1}]
    with pytest.raises(ValueError):
        create_sliding_window_segments(phrases, window_size=0)

def test_window_size_larger_than_list_raises():
    """window_size > number of phrases should raise ValueError."""
    phrases = [{"text": "Only one", "score": 1}]
    with pytest.raises(ValueError):
        create_sliding_window_segments(phrases, window_size=2)
