import pandas as pd
from flask import jsonify

def prepare_sentiment_chart_data(subject_news):
    # Ensure date column is datetime
    subject_news["date"] = pd.to_datetime(subject_news["date"], errors="coerce")
    subject_news = subject_news.dropna(subset=["date"])
    
    # Categorize sentiment
    def categorize(score):
        if score > 0:
            return "Positive"
        elif score < 0:
            return "Negative"
        else:
            return "Neutral"

    subject_news["SentimentCategory"] = subject_news["SentimentScore"].apply(categorize)

    # Group by date and sentiment
    sentiment_counts = (
        subject_news.groupby([subject_news["date"].dt.date, "SentimentCategory"])
        .size()
        .unstack(fill_value=0)
    )

    # Ensure all categories exist
    for cat in ["Positive", "Neutral", "Negative"]:
        if cat not in sentiment_counts:
            sentiment_counts[cat] = 0
    sentiment_counts = sentiment_counts[["Positive", "Neutral", "Negative"]]

    # Prepare JSON-like dict
    chart_data = {
        "dates": [str(d) for d in sentiment_counts.index],
        "positive": sentiment_counts["Positive"].tolist(),
        "neutral": sentiment_counts["Neutral"].tolist(),
        "negative": sentiment_counts["Negative"].tolist()
    }
    
    return chart_data
