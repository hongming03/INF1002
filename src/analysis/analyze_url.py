import re, requests
from datetime import datetime
from flask import render_template
from newspaper import Article
from analysis.segmentation import segment_text, all_segmentations, get_full_dictionary
from analysis.sentiment_analysis import analyze_text


def handle_analyze_url(query: str, force_segment: bool):
    """Handles scraping, segmentation, and sentiment analysis for /analyze_url."""

    if not query:
        return render_template("analyze_url.html", error="Please enter a valid URL or text.")

    article_text = ""
    article_title = "Raw Text Input"

    try:
        # --- Case 1: Handle full URL ---
        if re.match(r"^https?://", query):
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                )
            }

            if "127.0.0.1" in query or "localhost" in query:
                # Handle local demo page
                response = requests.get(query, headers=headers, timeout=8)
                html = response.text
                match = re.search(r"<p[^>]*>(.*?)</p>", html, re.DOTALL)
                article_text = match.group(1).strip() if match else ""
                article_title = "Crypto Sentiment Stress Test (Local Demo)"
            else:
                # External site scrape
                article_obj = Article(query)
                article_obj.download()
                article_obj.parse()
                article_text = article_obj.text or ""
                article_title = article_obj.title or "External Article"

            # Guard against invalid or non-article pages
            if not article_text.strip() or len(article_text.split()) < 20:
                return render_template(
                    "analyze_url.html",
                    error="The provided URL is not a readable article or contains too little text."
                )

        # --- Case 2: Plain text input ---
        else:
            article_text = query
            article_title = "Raw Text Input"

        # --- Segmentation (toggle-based) ---
        original_text = article_text
        one_seg = []
        all_segs = []

        if force_segment:
            dictionary = get_full_dictionary()
            text_lower = article_text.lower()

            # Always run single segmentation
            one_seg = segment_text(text_lower, dictionary)

            # Skip all_segmentations() for long text
            if len(text_lower) <= 60:
                try:
                    all_segs = all_segmentations(text_lower, dictionary)
                except Exception:
                    all_segs = []
            else:
                all_segs = []

            # Replace text only if segmentation succeeded
            if one_seg:
                article_text = " ".join(one_seg)

        # --- Sentiment Analysis ---
        if "Date:" not in article_text:
            article_text += f"\nDate: {datetime.today().strftime('%Y-%m-%d')}"

        phrase_results = analyze_text(article_text, mode="full")
        sentence_results = analyze_text(article_text, mode="sentence")
        sentiment_summary = sentence_results.get("summary", {})

        # --- Render Results ---
        return render_template(
            "analyze_url.html",
            article={
                "url": query if re.match(r"^https?://", query) else None,
                "title": article_title,
                "text": article_text,
                "source": "External" if re.match(r"^https?://", query) else "Manual Input",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "subject": "URL/Text Analysis"
            },
            original_text=original_text,
            one_seg=one_seg,
            all_segs=all_segs,
            sentiment_summary=sentiment_summary,
            most_positive=phrase_results["most_positive"],
            most_negative=phrase_results["most_negative"],
            most_positive_segment=phrase_results["most_positive_segment"],
            most_negative_segment=phrase_results["most_negative_segment"],
            most_positive_variable_segment=phrase_results["most_positive_variable_segment"],
            most_negative_variable_segment=phrase_results["most_negative_variable_segment"],
            force_segment = force_segment
        )

    except Exception as e:
        return render_template("analyze_url.html", error=f"Unexpected error: {e}")
