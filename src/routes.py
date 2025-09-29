# routes.py

# Standard library
import re
from urllib.parse import unquote

# Third-party libraries
from flask import render_template, redirect, url_for, request
from newspaper import Article

# Custom modules
from data.data_loader import CryptoNewsData
from analysis.sentiment_analysis import analyze_text
from analysis.segmentation import analyze_segmented_text, all_segmentations
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
    
    @app.route("/test-nospace")
    def test_nospace():
        # just render your template directly
        return render_template("article_nospace.html")



    @app.route("/analyze_url", methods=["GET", "POST"])
    def analyze_url():
        if request.method == "GET":
            return render_template("analyze_url.html")

        query = request.form.get("query", "").strip()
        if not query:
            return render_template("analyze_url.html", error="Please enter a valid URL or subject.")

        # -----------------------------------
        # If the query is a full URL
        # -----------------------------------
        if re.match(r"^https?://", query):
            try:
                article_obj = Article(query)
                article_obj.download()
                article_obj.parse()

                article_text = article_obj.text
                article_title = article_obj.title or "External Article"

                if not article_text:
                    return render_template("analyze_url.html", error="No readable article text found. Try another link.")

            except Exception as e:
                return render_template("analyze_url.html", error=f"Could not fetch article: {e}")

            # Run both sentence-level and phrase-level analysis
            phrase_results = analyze_text(article_text, mode="full")
            sentence_results = analyze_text(article_text, mode="sentence")
            sentiment_summary = sentence_results["summary"]

            return render_template(
                "analyze_url.html",
                article={
                    "url": query,
                    "title": article_title,
                    "text": article_text,
                    "source": "External",
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "subject": "URL Analysis"
                },
                sentiment_summary=sentiment_summary,
                most_positive=phrase_results["most_positive"],
                most_negative=phrase_results["most_negative"],
                most_positive_segment=phrase_results["most_positive_segment"],
                most_negative_segment=phrase_results["most_negative_segment"],
                most_positive_variable_segment=phrase_results["most_positive_variable_segment"],
                most_negative_variable_segment=phrase_results["most_negative_variable_segment"]
            )

        # -----------------------------------
        # If the query is a subject
        # -----------------------------------
        subjects = crypto_data.get_subjects()
        if query not in subjects:
            return render_template("analyze_url.html", error=f"'{query}' is not a valid subject or link.")

        return redirect(url_for("subject", subj=query))
    

    # for requirement 6
    @app.route("/segment_text", methods=["GET", "POST"])
    def segment_text_route():
        if request.method == "GET":
            return render_template("segment_text.html")

        raw_text = request.form.get("text", "").strip()

        if not raw_text:
            return render_template("segment_text.html", error="Please enter text without spaces.")

         # Use helper that already handles cleaning + sentiment analyzer
        result = analyze_segmented_text(raw_text)

        all_segs = all_segmentations(raw_text.lower()) if result["segmented"] else []
        one_seg = result["segmented"].split() if result["segmented"] else None
        score = result["score"]



        return render_template(
        "segment_text.html",
        text=raw_text,
        one_seg=result["segmented"].split() if result["segmented"] else None,
        all_segs=all_segs,
        score=result["score"]
        )

