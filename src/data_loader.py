import pandas as pd
from analyzer import SentimentAnalyzer
import os

class ReviewData:
    def __init__(self, csv_path=None):
        if csv_path is None:
            # Always use the path relative to this file
            csv_path = os.path.join(os.path.dirname(__file__), "Reviews_less.csv")
        self.csv_path = csv_path
        self.analyzer = SentimentAnalyzer()
        self.reviews = None

    # Create a new column called SentimentScore and populate it with Afinn.score
    def load_data(self):
        # Load CSV
        self.reviews = pd.read_csv(self.csv_path)
        self.reviews["Text"] = self.reviews["Text"].astype(str)
        # Compute sentiment scores
        self.reviews["SentimentScore"] = self.reviews["Text"].apply(self.analyzer.score)

    # Returns a list of unique product IDs
    def get_product_ids(self):
        if self.reviews is None:
            self.load_data()
        return self.reviews["ProductId"].unique().tolist()
    
    def get_reviews_by_user(self, user_id):
        if self.reviews is None:
            self.load_data()
        return self.reviews[self.reviews["UserId"] == user_id]

    # Returns average sentiment score and all reviews for a given product ID
    def get_reviews_by_product(self, product_id):
        if self.reviews is None:
            self.load_data()

        # Retrieving the reviews for the specified product ID
        product_reviews = self.reviews[self.reviews["ProductId"] == product_id]
        avg_score = product_reviews["SentimentScore"].mean()
        return avg_score, product_reviews
