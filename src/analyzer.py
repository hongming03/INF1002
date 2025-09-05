from afinn import Afinn

class SentimentAnalyzer:
    def __init__(self):
        # Initialize Afinn with English
        self.afinn = Afinn(language='en')

    def score(self, text: str) -> float:
        if not text:
            return 0
        # Afinn directly returns a sentiment score
        return self.afinn.score(text)
