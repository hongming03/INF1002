# analytics.py
import pandas as pd

def get_sentiment_summary(subject_news, avg_score):
    # Drop invalid dates
    subject_news["date"] = pd.to_datetime(subject_news["date"], errors="coerce")
    subject_news = subject_news.dropna(subset=["date"])

    positive = len(subject_news[subject_news["SentimentScore"] > 0])
    neutral = len(subject_news[subject_news["SentimentScore"] == 0])
    negative = len(subject_news[subject_news["SentimentScore"] < 0])

    most_positive = subject_news.loc[subject_news["SentimentScore"].idxmax()]
    most_negative = subject_news.loc[subject_news["SentimentScore"].idxmin()]

    return {
        "average_score": round(avg_score, 2),
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "most_positive": {"text": most_positive["text"], "SentimentScore": most_positive["SentimentScore"]},
        "most_negative": {"text": most_negative["text"], "SentimentScore": most_negative["SentimentScore"]}
    }

def get_chart_data(subject_news):
    # Ensure datetime
    subject_news["date"] = pd.to_datetime(subject_news["date"], errors="coerce")
    subject_news = subject_news.dropna(subset=["date"])

    # Average sentiment chart
    avg_chart_data = {
        "dates": subject_news["date"].dt.strftime("%Y-%m-%d").tolist(),
        "values": subject_news["SentimentScore"].tolist()
    }

    # POS/NEU/NEG chart
    def categorize(score):
        if score > 0: return "Positive"
        elif score < 0: return "Negative"
        else: return "Neutral"

    subject_news["SentimentCategory"] = subject_news["SentimentScore"].apply(categorize)
    sentiment_counts = subject_news.groupby([subject_news["date"].dt.date, "SentimentCategory"]).size().unstack(fill_value=0)

    for cat in ["Positive", "Neutral", "Negative"]:
        if cat not in sentiment_counts: sentiment_counts[cat] = 0
    sentiment_counts = sentiment_counts[["Positive", "Neutral", "Negative"]]

    area_chart_data = {
        "dates": [d.strftime("%Y-%m-%d") for d in sentiment_counts.index],
        "Positive": sentiment_counts["Positive"].tolist(),
        "Neutral": sentiment_counts["Neutral"].tolist(),
        "Negative": sentiment_counts["Negative"].tolist()
    }

    return avg_chart_data, area_chart_data
