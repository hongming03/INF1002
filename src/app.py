import pandas as pd
from flask import Flask, render_template, request
from data_loader import ReviewData
import os
import sys
from sentiment_analysis import analyze_sentences
from chart_generator import generate_sentiment_bar_chart

from analyzer import SentimentAnalyzer

app = Flask(__name__)

# review_data is the dataset + sentiment in a pandas DataFrame
review_data = ReviewData()

@app.route("/")
def home():
    product_ids = review_data.get_product_ids()
    return render_template("index.html", product_ids=product_ids)

@app.route("/product/<pid>")
def product(pid):
    # Get reviews (pandas dataframe) and average score for the selected product
    avg_score, product_reviews = review_data.get_reviews_by_product(pid)

    # Count the number of sentiments that is positive, neutral, and negative
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

    # Generate chart and get filename
    chart_filename = generate_sentiment_bar_chart(positive, neutral, negative, f"{pid}_sentiment_chart.png")

    # Render the product.html template with all data
    return render_template(
    "product.html",
    product_id=pid,
    sentiment_summary=sentiment_summary,
    reviews=reviews,
    chart_filename=chart_filename
    )

@app.route("/user_review/<userid>")
def user_review(userid):
    if review_data.reviews is None:
        review_data.load_data()

    analyzer = SentimentAnalyzer()
    user_reviews_df = review_data.get_reviews_by_user(userid)
    reviews = user_reviews_df.to_dict(orient="records")

    analysis = analyze_sentences(user_reviews_df["Text"].tolist(), analyzer)

    return render_template(
        "user_reviews.html",
        userid=userid,
        reviews=reviews,
        **analysis
    )


if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True, port=5000)
