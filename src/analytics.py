# analytics.py
import pandas as pd

def get_sentiment_summary(subject_news, avg_score):
    """
    Creates a summary of sentiment statistics for news articles
    """
    # Clean up dates - convert to datetime and remove invalid ones
    subject_news["date"] = pd.to_datetime(subject_news["date"], errors="coerce")
    subject_news = subject_news.dropna(subset=["date"])

    # Count how many articles are positive, neutral, and negative
    positive = len(subject_news[subject_news["SentimentScore"] > 0])
    neutral = len(subject_news[subject_news["SentimentScore"] == 0])
    negative = len(subject_news[subject_news["SentimentScore"] < 0])

    # Find the article with highest sentiment score
    most_positive = subject_news.loc[subject_news["SentimentScore"].idxmax()]
    # Find the article with lowest sentiment score
    most_negative = subject_news.loc[subject_news["SentimentScore"].idxmin()]

    # Return all the summary data as a dictionary
    return {
        "average_score": round(avg_score, 2),
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "most_positive": {"text": most_positive["text"], "SentimentScore": most_positive["SentimentScore"]},
        "most_negative": {"text": most_negative["text"], "SentimentScore": most_negative["SentimentScore"]}
    }

def get_chart_data(subject_news):
    """
    Prepares data for two types of charts: line chart and area chart
    """
    # Clean up dates - ensure they're in datetime format
    subject_news["date"] = pd.to_datetime(subject_news["date"], errors="coerce")
    subject_news = subject_news.dropna(subset=["date"])

    # Prepare data for line chart - shows sentiment scores over time
    avg_chart_data = {
        "dates": subject_news["date"].dt.strftime("%Y-%m-%d").tolist(),
        "values": subject_news["SentimentScore"].tolist()
    }

    # Helper function to convert sentiment scores to categories
    def categorize(score):
        if score > 0: return "Positive"
        elif score < 0: return "Negative"
        else: return "Neutral"

    # Add sentiment category column to the data
    subject_news["SentimentCategory"] = subject_news["SentimentScore"].apply(categorize)
    
    # Group by date and sentiment category, then count articles
    sentiment_counts = subject_news.groupby([subject_news["date"].dt.date, "SentimentCategory"]).size().unstack(fill_value=0)

    # Make sure all three categories exist (add them with 0 if missing)
    for cat in ["Positive", "Neutral", "Negative"]:
        if cat not in sentiment_counts: sentiment_counts[cat] = 0
    sentiment_counts = sentiment_counts[["Positive", "Neutral", "Negative"]]

    # Prepare data for area chart - shows count of each sentiment category over time
    area_chart_data = {
        "dates": [d.strftime("%Y-%m-%d") for d in sentiment_counts.index],
        "Positive": sentiment_counts["Positive"].tolist(),
        "Neutral": sentiment_counts["Neutral"].tolist(),
        "Negative": sentiment_counts["Negative"].tolist()
    }

    # Return both chart data sets
    return avg_chart_data, area_chart_data