import pandas as pd
from flask import Flask, render_template, request
from data_loader import CryptoNewsData 
import os
import sys
from sentiment_analysis import analyze_sentences
from urllib.parse import unquote
import json

from analyzer import SentimentAnalyzer

app = Flask(__name__)

# crypto_data is the dataset + sentiment in a pandas DataFrame
crypto_data = CryptoNewsData()

@app.route("/")
def home():
    subjects = crypto_data.get_subjects()

    # Add empty defaults so template doesn't break
    avg_chart_data = {"dates": [], "values": []}
    area_chart_data = {"dates": [], "positive": [], "neutral": [], "negative": []}

    return render_template(
        "index.html",
        subjects=subjects,
        avg_chart_data=avg_chart_data,
        area_chart_data=area_chart_data
    )

import json

@app.route("/subject/<subj>")
def subject(subj):
    avg_score, subject_news = crypto_data.get_news_by_subject(subj)

    # Convert date column to datetime and drop invalid rows
    subject_news["date"] = pd.to_datetime(subject_news["date"], errors="coerce")
    subject_news = subject_news.dropna(subset=["date"])

    positive = len(subject_news[subject_news["SentimentScore"] > 0])
    neutral = len(subject_news[subject_news["SentimentScore"] == 0])
    negative = len(subject_news[subject_news["SentimentScore"] < 0])

    # Most positive and most negative
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

    # Prepare JSON data for Chart.js
    avg_chart_data = {
        "dates": subject_news["date"].dt.strftime("%Y-%m-%d").tolist(),
        "values": subject_news["SentimentScore"].tolist()
    }

    # Prepare counts for POS/NEU/NEG stacked chart
    def categorize(score):
        if score > 0:
            return "Positive"
        elif score < 0:
            return "Negative"
        else:
            return "Neutral"

    subject_news["SentimentCategory"] = subject_news["SentimentScore"].apply(categorize)
    sentiment_counts = subject_news.groupby(
        [subject_news["date"].dt.date, "SentimentCategory"]
    ).size().unstack(fill_value=0)

    for cat in ["Positive", "Neutral", "Negative"]:
        if cat not in sentiment_counts:
            sentiment_counts[cat] = 0
    sentiment_counts = sentiment_counts[["Positive", "Neutral", "Negative"]]

    area_chart_data = {
        "dates": [d.strftime("%Y-%m-%d") for d in sentiment_counts.index],
        "Positive": sentiment_counts["Positive"].tolist(),
        "Neutral": sentiment_counts["Neutral"].tolist(),
        "Negative": sentiment_counts["Negative"].tolist()
    }

    subjects = crypto_data.get_subjects()

    return render_template(
        "index.html",
        subject=subj,
        sentiment_summary=sentiment_summary,
        articles=articles,
        avg_chart_data=avg_chart_data,
        area_chart_data=area_chart_data,
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
