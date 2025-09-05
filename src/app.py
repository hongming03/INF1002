import pandas as pd
from flask import Flask, render_template, request
from data_loader import ReviewData
import os
import sys

from analyzer import SentimentAnalyzer

app = Flask(__name__)

review_data = ReviewData()

@app.route("/")
def home():
    product_ids = review_data.get_product_ids()
    return render_template("index.html", product_ids=product_ids)

@app.route("/product/<pid>")
def product(pid):

    # avg_score, product_reviews = review_data.get_reviews_by_product(selected_product)

    #     # Compute counts for positive/neutral/negative reviews
    #     positive = len(product_reviews[product_reviews["SentimentScore"] > 0])
    #     neutral = len(product_reviews[product_reviews["SentimentScore"] == 0])
    #     negative = len(product_reviews[product_reviews["SentimentScore"] < 0])

    #     sentiment_summary = {
    #         "average_score": round(avg_score, 2),
    #         "positive": positive,
    #         "neutral": neutral,
    #         "negative": negative
    #     }

    return f"Product ID: {pid}"

if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True, port=5000)
