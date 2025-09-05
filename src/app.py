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
    # Get reviews and average score for the selected product
    avg_score, product_reviews = review_data.get_reviews_by_product(pid)

    # Compute sentiment counts
    positive = len(product_reviews[product_reviews["SentimentScore"] > 0])
    neutral = len(product_reviews[product_reviews["SentimentScore"] == 0])
    negative = len(product_reviews[product_reviews["SentimentScore"] < 0])

    # Prepare summary dictionary
    sentiment_summary = {
        "average_score": round(avg_score, 2),
        "positive": positive,
        "neutral": neutral,
        "negative": negative
    }

    # Convert reviews to list of dicts for Jinja rendering
    reviews = product_reviews.to_dict(orient="records")

    # Render the product.html template with all data
    return render_template(
        "product.html",
        product_id=pid,
        sentiment_summary=sentiment_summary,
        reviews=reviews
    )


if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True, port=5000)
