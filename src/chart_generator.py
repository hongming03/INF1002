import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

def generate_sentiment_bar_chart(positive, neutral, negative, output_filename):
    categories = ['Positive', 'Neutral', 'Negative']
    counts = [positive, neutral, negative]
    colors = ['#2ca02c', '#ff7f0e', '#d62728']

    plt.style.use('seaborn-v0_8')
    fig, ax = plt.subplots()

    ax.bar(categories, counts, color=colors)
    ax.set_ylabel('Number of Reviews', color='black')
    ax.set_title('Review Sentiment Distribution', color='black')

    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.tick_params(colors='black')
    for spine in ax.spines.values():
        spine.set_color('black')

    plt.tight_layout()

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)

    output_path = os.path.join(static_dir, output_filename)
    plt.savefig(output_path, transparent=True)
    plt.close()
    return output_filename
