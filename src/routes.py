# routes.py

# Standard library
import re, requests
from urllib.parse import unquote
from datetime import datetime

# Third-party libraries
from flask import render_template, redirect, url_for, request
from newspaper import Article

# Custom modules
from data.data_loader import CryptoNewsData
from analysis.sentiment_analysis import analyze_text
from analysis.analyze_url import handle_analyze_url
from reporting.analytics import get_sentiment_summary, get_chart_data


import pandas as pd
from datetime import datetime

crypto_data = CryptoNewsData()

def register_routes(app):

    @app.route("/")
    def home():
        subjects = crypto_data.get_subjects()
        return render_template(
            "index.html",
            subjects=subjects,
            avg_chart_data={"dates": [], "values": []},
            area_chart_data={"dates": [], "Positive": [], "Neutral": [], "Negative": []}
        )
    
    # Return a OK response body and 200 status code for health checks
    @app.route("/health")
    def health():
        return "OK", 200

    @app.route("/subject/<subj>")
    def subject(subj):
        avg_score, subject_news = crypto_data.get_news_by_subject(subj)

        sentiment_summary = get_sentiment_summary(subject_news, avg_score)
        avg_chart_data, area_chart_data = get_chart_data(subject_news)

        subjects = crypto_data.get_subjects()
        articles = subject_news.to_dict(orient="records")

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
        url = unquote(url_encoded)
        if crypto_data.news is None:
            crypto_data.load_data()

        article_df = crypto_data.news[crypto_data.news["url"] == url]
        if article_df.empty:
            return "Article not found", 404

        article = article_df.iloc[0]
        results = analyze_text(article["text"], mode="full")
        subjects = crypto_data.get_subjects()

        return render_template(
            "article_sentiment.html",
            article=article,
            subjects=subjects,
            most_positive=results["most_positive"],
            most_negative=results["most_negative"],
            most_positive_segment=results["most_positive_segment"],
            most_negative_segment=results["most_negative_segment"],
            most_positive_variable_segment=results["most_positive_variable_segment"],
            most_negative_variable_segment=results["most_negative_variable_segment"]
        )
    
    #test scenario for webpage segemnmtation.
    @app.route("/test-nospace")
    def test_nospace():
        return render_template("article_nospace.html")


    #Web Scrape
    @app.route("/analyze_url", methods=["GET", "POST"])
    def analyze_url():
        if request.method == "GET":
            return render_template("analyze_url.html")

        query = request.form.get("query", "").strip()
        force_segment = bool(request.form.get("force_segment"))

        # call the analyze_url handler
        return handle_analyze_url(query, force_segment)

