# analytics.py
import pandas as pd

def get_sentiment_summary(subject_news, avg_score):
    """
    Build a quick summary of sentiment stats for a bunch of news articles
    """

    # Convert "date" column into proper datetime (drop rows with bad dates)
    subject_news["date"] = pd.to_datetime(subject_news["date"], errors="coerce")
    subject_news = subject_news.dropna(subset=["date"])

    # Count articles by sentiment type
    positive = len(subject_news[subject_news["SentimentScore"] > 0])
    neutral = len(subject_news[subject_news["SentimentScore"] == 0])
    negative = len(subject_news[subject_news["SentimentScore"] < 0])

    # Find the articles with the strongest positive/negative scores
    most_positive = subject_news.loc[subject_news["SentimentScore"].idxmax()]
    most_negative = subject_news.loc[subject_news["SentimentScore"].idxmin()]

    # Package everything into a dictionary for easy use later
    return {
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


def get_chart_data(subject_news):
    """
    Prepare the data needed for a line chart and an area chart
    """

    # Clean up dates
    subject_news["date"] = pd.to_datetime(subject_news["date"], errors="coerce")
    subject_news = subject_news.dropna(subset=["date"])

    # Line chart data: plot sentiment scores over time
    avg_chart_data = {
        "dates": subject_news["date"].dt.strftime("%Y-%m-%d").tolist(),
        "values": subject_news["SentimentScore"].tolist()
    }

    # Quick helper to label each score as Positive/Neutral/Negative
    def categorize(score):
        if score > 0:
            return "Positive"
        elif score < 0:
            return "Negative"
        else:
            return "Neutral"

    subject_news["SentimentCategory"] = subject_news["SentimentScore"].apply(categorize)

    # Count how many of each category appear on each date
    sentiment_counts = (
        subject_news
        .groupby([subject_news["date"].dt.date, "SentimentCategory"])
        .size()
        .unstack(fill_value=0)
    )

    # Make sure all 3 categories exist, even if count = 0
    for cat in ["Positive", "Neutral", "Negative"]:
        if cat not in sentiment_counts:
            sentiment_counts[cat] = 0

    # Keep the order consistent
    sentiment_counts = sentiment_counts[["Positive", "Neutral", "Negative"]]

    # Area chart data: stacked counts over time
    area_chart_data = {
        "dates": [d.strftime("%Y-%m-%d") for d in sentiment_counts.index],
        "Positive": sentiment_counts["Positive"].tolist(),
        "Neutral": sentiment_counts["Neutral"].tolist(),
        "Negative": sentiment_counts["Negative"].tolist()
    }

    return avg_chart_data, area_chart_data
