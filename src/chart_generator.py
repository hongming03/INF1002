import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def generate_sentiment_line_chart(subject_news, output_filename):


    # Ensure date column is datetime
    subject_news["date"] = pd.to_datetime(
    subject_news["date"], errors="coerce", infer_datetime_format=True
    )

    # Group by date (you can choose daily, weekly, etc.)
    sentiment_over_time = (
        subject_news.groupby(subject_news["date"].dt.date)["SentimentScore"].mean()
    )

    plt.style.use('seaborn-v0_8')
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(sentiment_over_time.index, sentiment_over_time.values, marker="o", color="blue")

    ax.set_ylabel("Average Sentiment Score", color="black")
    ax.set_title("Average Sentiment Over Time", color="black")

    # Format x-axis for readability
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    ax.tick_params(colors='black')

    for spine in ax.spines.values():
        spine.set_color("black")

    plt.tight_layout()

    # Save into static/img/matplotlib
    static_subdir = os.path.join("static", "img", "matplotlib")
    static_dir = os.path.join(os.path.dirname(__file__), static_subdir)
    os.makedirs(static_dir, exist_ok=True)

    output_path = os.path.join(static_dir, output_filename)
    plt.savefig(output_path, transparent=True)
    plt.close()

    return f"img/matplotlib/{output_filename}"

def generate_sentiment_count_area_chart(subject_news, output_filename):
    """
    Creates a stacked area chart showing counts of Positive, Neutral, Negative articles over time.
    """

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
    sentiment_counts = subject_news.groupby([subject_news["date"].dt.date, "SentimentCategory"]).size().unstack(fill_value=0)

    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(10, 4))

    # Ensure all categories exist
    for cat in ["Positive", "Neutral", "Negative"]:
        if cat not in sentiment_counts:
            sentiment_counts[cat] = 0

    sentiment_counts = sentiment_counts[["Positive", "Neutral", "Negative"]]

    # Plot stacked area chart
    ax.stackplot(
        sentiment_counts.index,
        sentiment_counts["Positive"],
        sentiment_counts["Neutral"],
        sentiment_counts["Negative"],
        labels=["Positive", "Neutral", "Negative"],
        colors=["#2ca02c", "#ff7f0e", "#d62728"],
        alpha=0.8
    )

    ax.set_ylabel("Number of Articles", color="black")
    ax.set_title("Sentiment Counts Over Time", color="black")

    # Legend with black text
    legend = ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="black", fontsize=10)
    for text in legend.get_texts():
        text.set_color("black")

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.tick_params(axis="x", colors="black", rotation=45)
    ax.tick_params(axis="y", colors="black")
    
    # Spines
    for spine in ax.spines.values():
        spine.set_color("black")

    plt.tight_layout()

    # Save chart
    static_subdir = os.path.join("static", "img", "matplotlib")
    static_dir = os.path.join(os.path.dirname(__file__), static_subdir)
    os.makedirs(static_dir, exist_ok=True)
    output_path = os.path.join(static_dir, output_filename)
    plt.savefig(output_path, transparent=True)
    plt.close()

    return f"img/matplotlib/{output_filename}"

