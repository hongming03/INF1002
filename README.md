# Sentiment Analysis on Crypto News Article

Brief description of what your project does and its main purpose in 1-2 sentences.

## Features

- Web scrapes crypto news articles from user-provided URLs
- Performs sentiment analysis (Positive/Neutral/Negative) on article content
- Applies sliding window technique to identify most positive/negative segments
- Processes crypto news article datasets for batch analysis
- Plots sentiment trends over time with interactive visualizations
- Flask web interface for easy interaction
- Real-time sentiment scoring and analysis

## Requirements

- Python 3.7+
- pip (Python package manager)
- Docker (optional)

## Installation & Setup

### Option 1: Local Python Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd INF1002
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python src/app.py
   ```

### Option 2: Docker Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd INF1002
   ```

2. **Build and run with Docker**
   ```bash
   docker build -t your-app-name .
   docker run -p 5000:5000 your-app-name
   ```
