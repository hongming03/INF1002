import pandas as pd
from flask import Flask, render_template, request
from data_loader import CryptoNewsData 
import os
import sys
from sentiment_analysis import analyze_sentences
from chart_generator import generate_sentiment_bar_chart
from urllib.parse import unquote

from analyzer import SentimentAnalyzer

app = Flask(__name__)

# crypto_data is the dataset + sentiment in a pandas DataFrame
crypto_data = CryptoNewsData()

@app.route("/")
def home():
    subjects = crypto_data.get_subjects()
    return render_template("index.html", subjects=subjects)

@app.route("/subject/<subj>")
def subject(subj):
    avg_score, subject_news = crypto_data.get_news_by_subject(subj)

    positive = len(subject_news[subject_news["SentimentScore"] > 0])
    neutral = len(subject_news[subject_news["SentimentScore"] == 0])
    negative = len(subject_news[subject_news["SentimentScore"] < 0])

    # Find most positive and most negative article
    most_positive = subject_news.loc[subject_news["SentimentScore"].idxmax()]
    most_negative = subject_news.loc[subject_news["SentimentScore"].idxmin()]

    sentiment_summary = {
        "average_score": round(avg_score, 2),
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "most_positive": {
            "text": most_positive["text"],
            "SentimentScore": most_positive["SentimentScore"]
        },
        "most_negative": {
            "text": most_negative["text"],
            "SentimentScore": most_negative["SentimentScore"]
        }
    }

    articles = subject_news.to_dict(orient="records")
    chart_filename = generate_sentiment_bar_chart(
        positive, neutral, negative, f"{subj}_sentiment_chart.png"
    )

    subjects = crypto_data.get_subjects()

    return render_template(
        "index.html",
        subject=subj,
        sentiment_summary=sentiment_summary,
        articles=articles,
        chart_filename=chart_filename,
        subjects=subjects
    )


@app.route("/article/<path:url_encoded>")
def article_sentiment(url_encoded):
    # Decode URL
    url = unquote(url_encoded)

    if crypto_data.news is None:
        crypto_data.load_data()

    # Get the article row
    article_df = crypto_data.news[crypto_data.news["url"] == url]
    if article_df.empty:
        return "Article not found", 404

    article = article_df.iloc[0]

    analyzer = SentimentAnalyzer()
    analysis = analyze_sentences([article["text"]], analyzer)

    subjects = crypto_data.get_subjects()

    return render_template(
        "article_sentiment.html",
        article=article,
        subjects=subjects,
        **analysis
    )


if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True, port=5000)
