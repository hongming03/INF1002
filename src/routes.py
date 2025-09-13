# routes.py
from flask import render_template
from data_loader import CryptoNewsData
from analytics import get_sentiment_summary, get_chart_data
from sentiment_analysis import analyze_sentences
from analyzer import SentimentAnalyzer
from urllib.parse import unquote
import re
from flask import request, redirect, url_for
import requests
from newspaper import Article
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

    @app.route("/subject/<subj>")
    def subject(subj):
        avg_score, subject_news = crypto_data.get_news_by_subject(subj)

        # Use analytics module
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
        analyzer = SentimentAnalyzer()
        analysis = analyze_sentences([article["text"]], analyzer)
        subjects = crypto_data.get_subjects()

        return render_template(
            "article_sentiment.html",
            article=article,
            subjects=subjects,
            **analysis
        )
    

    #analyze url based on user input
    @app.route("/analyze_url", methods=["GET", "POST"])
    def analyze_url():
        if request.method == "GET":
            return render_template("analyze_url.html")

        query = request.form.get("query")
        if not query:
            return render_template("analyze_url.html", error="⚠️ Please enter a URL or subject.")

        # If it's a URL
        if re.match(r"^https?://", query):
            try:
                article_obj = Article(query)
                article_obj.download()
                article_obj.parse()
                article_text = article_obj.text
                article_title = article_obj.title
            except Exception as e:
                return render_template("analyze_url.html", error=f"⚠️ Could not fetch article: {e}")

            if not article_text.strip():
                return render_template("analyze_url.html", error="⚠️ No readable article text found. Try another link.")

            # Run existing sentiment analyzer
            analyzer = SentimentAnalyzer()
            analysis = analyze_sentences([article_text], analyzer)

            # Convert analysis into DataFrame
            if isinstance(analysis, list):  
                # assume it's a list of dicts with 'text' + 'SentimentScore'
                df = pd.DataFrame(analysis)
            elif isinstance(analysis, dict):
                # fallback: wrap dict
                df = pd.DataFrame([analysis])
            else:
                return render_template("analyze_url.html", error="⚠️ Unexpected analysis format.")

            # Ensure required columns
            if "text" not in df:
                df["text"] = article_text
            if "SentimentScore" not in df:
                return render_template("analyze_url.html", error="⚠️ Analysis did not return sentiment scores.")
            df["date"] = datetime.today().strftime("%Y-%m-%d")

            # Build sentiment summary + chart data
            avg_score = df["SentimentScore"].mean()
            sentiment_summary = get_sentiment_summary(df, avg_score)
            avg_chart_data, area_chart_data = get_chart_data(df)

            return render_template(
                "analyze_url.html",
                article={"url": query, "title": article_title or "External Article", "text": article_text},
                sentiment_summary=sentiment_summary,
                avg_chart_data=avg_chart_data,
                area_chart_data=area_chart_data
            )

        # Not a URL → check valid subject
        subjects = crypto_data.get_subjects()
        if query not in subjects:
            return render_template("analyze_url.html", error=f" '{query}' is not a valid subject or link.")

        return redirect(url_for("subject", subj=query))
