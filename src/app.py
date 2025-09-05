import pandas as pd
from flask import Flask, render_template, request
from data_loader import ReviewData
import os
import sys
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')

from analyzer import SentimentAnalyzer

app = Flask(__name__)

#review_data is a pandas DataFrame
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

@app.route("/user_review/<userid>")
def user_review(userid):
    if review_data.reviews is None:
        review_data.load_data()

    analyzer = SentimentAnalyzer()
    user_reviews_df = review_data.get_reviews_by_user(userid)
    reviews = user_reviews_df.to_dict(orient="records")

    all_sentences = []
    for review in reviews:
        # Rough sentence split using period
        sentences = review["Text"].split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:  # Skip empty strings
                score = analyzer.score(sentence)
                all_sentences.append({"text": sentence, "score": score})

    # Sort sentences by score
    most_positive = max(all_sentences, key=lambda x: x["score"], default=None)
    most_negative = min(all_sentences, key=lambda x: x["score"], default=None)

    # Sliding window (3 sentences per segment)
    window_size = 3
    segments = []
    for i in range(len(all_sentences) - window_size + 1):
        segment = all_sentences[i:i+window_size]
        segment_text = ". ".join([s["text"] for s in segment]) + "."
        segment_score = sum([s["score"] for s in segment])
        segments.append({"text": segment_text, "score": segment_score})

    most_positive_segment = max(segments, key=lambda x: x["score"], default=None)
    most_negative_segment = min(segments, key=lambda x: x["score"], default=None)

    return render_template(
        "user_reviews.html",
        userid=userid,
        reviews=reviews,
        most_positive=most_positive,
        most_negative=most_negative,
        most_positive_segment=most_positive_segment,
        most_negative_segment=most_negative_segment
    )

if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True, port=5000)
