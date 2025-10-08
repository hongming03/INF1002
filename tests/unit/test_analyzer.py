import pytest
from unittest.mock import mock_open, patch
from src.models.analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    """Unit tests for SentimentAnalyzer class
    
    Example Trace:
    text = "I love cats!"
    Tokenized → ["i", "love", "cats"]
    Dictionary lookup → "i":0, "love":3, "cats":2
    Score → 0 + 3 + 2 = 5
    """
    
    @pytest.fixture
    def mock_afinn_data(self):
        """Mock AFINN dictionary data for testing"""
        return "happy\t3\ngood\t3\nbad\t-3\nterrible\t-4\nlove\t3\ncats\t2\n"
    
    @pytest.fixture
    def analyzer(self, mock_afinn_data):
        """Create a SentimentAnalyzer instance with mocked AFINN data"""
        with patch('builtins.open', mock_open(read_data=mock_afinn_data)):
            return SentimentAnalyzer('fake/path.txt')
    
    def test_score_example_trace(self, analyzer):
        """Test the example trace: 'I love cats!'
        
        Expected flow:
        - Tokenized → ["i", "love", "cats"]
        - Dictionary lookup → "i":0, "love":3, "cats":2
        - Score → 0 + 3 + 2 = 5
        """
        score = analyzer.score("I love cats!")
        assert score == 5
    
    def test_score_empty_text(self, analyzer):
        """Edge Case: Empty text should return 0"""
        score = analyzer.score("")
        assert score == 0
    
    def test_score_words_not_in_dictionary(self, analyzer):
        """Edge Case: Words not in dictionary contribute 0 to total score"""
        score = analyzer.score("xyz abc qwerty")
        assert score == 0
    
    def test_score_text_with_punctuation(self, analyzer):
        """Edge Case: Punctuation is ignored during tokenization"""
        score = analyzer.score("This is good!!!")
        # 'good' = 3, punctuation ignored
        assert score == 3
    
    def test_score_mixed_sentiment(self, analyzer):
        """Test scoring with both positive and negative words"""
        score = analyzer.score("This is good but terrible")
        # 'good' = 3, 'terrible' = -4
        assert score == -1