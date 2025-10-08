import re, requests
from datetime import datetime
from flask import render_template
from newspaper import Article
from analysis.segmentation import segment_text, get_full_dictionary
from analysis.sentiment_analysis import analyze_text


def handle_analyze_url(query: str, force_segment: bool):
    """Handles scraping, segmentation, and sentiment analysis for /analyze_url."""

    # --- Validate input ---
    if not query:
        return render_template("analyze_url.html", error="Please enter a valid URL or text.")

    # Catch malformed URL like 'htt://'
    if query.startswith("http") and not re.match(r"^https?://", query):
        return render_template(
            "analyze_url.html",
            error="Invalid URL format. Please include http:// or https://"
        )

    article_text = ""
    article_title = "Raw Text Input"

    try:
        # --- Case 1: Handle full URL ---
        if re.match(r"^https?://", query):
            if "127.0.0.1" in query or "localhost" in query:
                # Handle local demo page
                response = requests.get(query, timeout=8)
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

            # Guard against invalid or non-article pages (skip localhost)
            if not article_text.strip() or (
                len(article_text.split()) < 20
                and "127.0.0.1" not in query
                and "localhost" not in query
            ):
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

        if force_segment:
            dictionary = get_full_dictionary()
            text_lower = article_text.lower()

            one_seg = segment_text(text_lower, dictionary)

            # Gibberish handling. discard mostly single letters or nonsense
            if one_seg:
                total_words = len(one_seg)
                single_letters = sum(len(w) == 1 for w in one_seg)
                avg_len = sum(len(w) for w in one_seg) / total_words if total_words else 0

                # skip segmentation if >50% are single letters OR avg word < 3
                if single_letters / total_words < 0.5 and avg_len >= 3:
                    article_text = " ".join(one_seg)
                else:
                    one_seg = []  # discard as gibberish

        # --- Sentiment Analysis ---
        if "Date:" not in article_text:
            article_text += f"\nDate: {datetime.today().strftime('%Y-%m-%d')}"

        phrase_results = analyze_text(article_text, mode="full")
        sentence_results = analyze_text(article_text, mode="sentence")
        sentiment_summary = sentence_results.get("summary", {})

        # Handle case where all scores are neutral or negative
        most_pos = sentiment_summary.get("most_positive", {}).get("SentimentScore", 0)
        most_neg = sentiment_summary.get("most_negative", {}).get("SentimentScore", 0)

        # If both positive and negative are <= 0, replace positive text with message
        if most_pos <= 0 and most_neg <= 0:
            sentiment_summary["most_positive"]["text"] = "No clearly positive sentence found."
            sentiment_summary["most_positive"]["SentimentScore"] = 0

        # 🧠 only one sentence exists or both pos/neg are identical, adjust labels
        pos_text = sentiment_summary.get("most_positive", {}).get("text", "").strip().lower()
        neg_text = sentiment_summary.get("most_negative", {}).get("text", "").strip().lower()

        if pos_text and neg_text and pos_text == neg_text:
            sentiment_summary["most_negative"]["text"] = "No distinctly negative sentence found."
            sentiment_summary["most_negative"]["SentimentScore"] = 0


        # Remove injected date from text and analyzer results
        article_text = re.sub(r"\s*Date:\s*\d{4}-\d{2}-\d{2}\s*$", "", article_text).strip()

        # Clean all possible text fields in results (including variable-length segments)
        for result_block in [phrase_results, sentiment_summary]:
            for key, block in result_block.items():
                if isinstance(block, dict) and "text" in block:
                    block["text"] = re.sub(r"Date[:\s\d\-]*", "", block["text"]).strip()

        # Specifically clean variable-length segment results if 'Date' slipped through
        for key in [
            "most_positive_variable_segment",
            "most_negative_variable_segment",
        ]:
            if key in phrase_results:
                seg = phrase_results[key]
                if isinstance(seg, dict) and "text" in seg:
                    text = seg["text"].strip()
                    if re.fullmatch(r"Date[:\s\d\-]*", text) or not re.search(r"[a-zA-Z]", text):
                        phrase_results[key] = {"text": "", "score": 0}


        # --- Render Results ---
        return render_template(
            "analyze_url.html",
            article={
                "url": query if re.match(r"^https?://", query) else None,
                "title": article_title,
                "text": article_text,
                "source": "External" if re.match(r"^https?://", query) else "Manual Input",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "subject": "URL/Text Analysis",
            },
            original_text=original_text,
            one_seg=one_seg,
            sentiment_summary=sentiment_summary,
            most_positive=phrase_results["most_positive"],
            most_negative=phrase_results["most_negative"],
            most_positive_segment=phrase_results["most_positive_segment"],
            most_negative_segment=phrase_results["most_negative_segment"],
            most_positive_variable_segment=phrase_results["most_positive_variable_segment"],
            most_negative_variable_segment=phrase_results["most_negative_variable_segment"],
            force_segment=force_segment
        )

    except Exception as e:
        error_message = str(e)
        if "403" in error_message or "Forbidden" in error_message:
            return render_template(
                "analyze_url.html",
                error="This website does not support automatic scraping. You can still analyze the text manually by pasting it below."
            )
        elif "404" in error_message:
            return render_template(
                "analyze_url.html",
                error="The article could not be found (404). Please check the URL or paste the text manually."
            )
        else:
            return render_template(
                "analyze_url.html",
                error="Unable to fetch the article. Please paste the text manually for analysis."
            )

