import os
from flask import Flask, request, jsonify, render_template
from analyzer import SentimentAnalyzer

app = Flask(__name__, template_folder='templates')

# Path to your Amazon reviews dataset
dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dataset/test_less.ft.txt'))


# Initialize analyzer (uses Afinn module internally)
analyzer = SentimentAnalyzer()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    text = request.form.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    analysis_results = analyzer.analyze_text(text)
    window_results = analyzer.sliding_window_analysis(text)

    return jsonify({
        'type': 'text_analysis',
        'overall': {
            'total_score': analysis_results['total_score'],
            'avg_score': round(analysis_results['avg_score'], 2),
            'num_sentences': len(analysis_results['sentences'])
        },
        'sentences': [{'text': s, 'score': score} for s, score in zip(
            analysis_results['sentences'], analysis_results['sentence_scores'])],
        'most_positive_sentence': analysis_results['most_positive_sentence'],
        'most_negative_sentence': analysis_results['most_negative_sentence'],
        'most_positive_window': window_results['most_positive'],
        'most_negative_window': window_results['most_negative']
    })

@app.route('/analyze-dataset', methods=['POST'])
def analyze_dataset():
    if not os.path.exists(dataset_path):
        return jsonify({'error': f'Dataset file not found at path: {dataset_path}'}), 400

    dataset_results = analyzer.process_dataset(dataset_path)
    if 'error' in dataset_results:
        return jsonify({'error': dataset_results['error']}), 500

    return jsonify({
        'type': 'dataset_analysis',
        'total_reviews': dataset_results['total_reviews_processed'],
        'most_positive_review': dataset_results['most_positive_review'],
        'most_negative_review': dataset_results['most_negative_review']
    })

if __name__ == '__main__':
    app.run(debug=True)
