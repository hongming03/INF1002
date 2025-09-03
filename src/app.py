# src/app.py

import os
from flask import Flask, request, jsonify, render_template
from analyzer import SentimentAnalyzer
import config

app = Flask(__name__)

# Initialize the analyzer with the AFINN file path from the config file
analyzer = SentimentAnalyzer(config.AFINN_PATH)

@app.route('/')
def home():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    """Endpoint to analyze custom text from the frontend."""
    text = request.form.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    analysis_results = analyzer.analyze_text(text)
    window_results = analyzer.sliding_window_analysis(text)

    response_data = {
        'type': 'text_analysis',
        'overall': {
            'total_score': analysis_results['total_score'],
            'avg_score': round(analysis_results['avg_score'], 2),
            'num_sentences': len(analysis_results['sentences'])
        },
        'sentences': [{
            'text': s,
            'score': score
        } for s, score in zip(analysis_results['sentences'], analysis_results['sentence_scores'])],
        'most_positive_sentence': analysis_results['most_positive_sentence'],
        'most_negative_sentence': analysis_results['most_negative_sentence'],
        'most_positive_window': window_results['most_positive'],
        'most_negative_window': window_results['most_negative']
    }
    
    return jsonify(response_data)

@app.route('/analyze-dataset', methods=['POST'])
def analyze_dataset():
    """Endpoint to analyze a dataset file."""
    
    if not os.path.exists(config.DATASET_PATH):
        return jsonify({'error': f'Dataset file not found at path: {config.DATASET_PATH}'}), 400
    
    dataset_results = analyzer.process_dataset(config.DATASET_PATH)
    
    if 'error' in dataset_results:
        return jsonify({'error': dataset_results['error']}), 500

    response_data = {
        'type': 'dataset_analysis',
        'total_reviews': dataset_results['total_reviews_processed'],
        'most_positive_review': dataset_results['most_positive_review'],
        'most_negative_review': dataset_results['most_negative_review']
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
