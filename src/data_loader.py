import pandas as pd
from analyzer import SentimentAnalyzer
import os

class CryptoNewsData:
    def __init__(self, csv_path=None):
        if csv_path is None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(BASE_DIR, "data", "cryptonews.csv")
        self.csv_path = csv_path
        self.analyzer = SentimentAnalyzer()
        self.news = None

    # Create a new Sentiment Column with Afinn scores
    def load_data(self):
        # Load CSV
        self.news = pd.read_csv(self.csv_path)

        # Ensure text is string
        self.news["text"] = self.news["text"].astype(str)

        # Use Afinn to compute sentiment score
        self.news["SentimentScore"] = self.news["text"].apply(self.analyzer.score)

    # Returns a list of unique subjects (instead of ProductIds)
    def get_subjects(self):
        if self.news is None:
            self.load_data()
        return self.news["subject"].unique().tolist()
    
    # Returns all news from a given source
    def get_news_by_source(self, source):
        if self.news is None:
            self.load_data()
        return self.news[self.news["source"] == source]

    # Returns average sentiment score and articles for a given subject
    def get_news_by_subject(self, subject):
        if self.news is None:
            self.load_data()
        subject_news = self.news[self.news["subject"] == subject]
        avg_score = subject_news["SentimentScore"].mean()
        return avg_score, subject_news
