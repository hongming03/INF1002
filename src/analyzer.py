import re
import statistics
from afinn import Afinn

class SentimentAnalyzer:
    """Sentiment analysis using Afinn module (English AFINN-111)."""
    def __init__(self):
        self.afinn = Afinn()

    def clean_text(self, text):
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text.split()

    def get_sentence_score(self, sentence):
        return self.afinn.score(sentence)

    def split_into_sentences(self, text):
        sentences = re.split(r'(?<!\d)[.!?]+\s*', text)
        return [s.strip() for s in sentences if s.strip()]

    def analyze_text(self, text):
        sentences = self.split_into_sentences(text)
        if not sentences:
            return {'sentences': [], 'sentence_scores': [], 'most_positive_sentence': None,
                    'most_negative_sentence': None, 'avg_score': 0, 'total_score': 0}

        sentence_scores = [self.get_sentence_score(s) for s in sentences]
        max_idx = sentence_scores.index(max(sentence_scores))
        min_idx = sentence_scores.index(min(sentence_scores))

        return {
            'sentences': sentences,
            'sentence_scores': sentence_scores,
            'most_positive_sentence': (sentences[max_idx], sentence_scores[max_idx]),
            'most_negative_sentence': (sentences[min_idx], sentence_scores[min_idx]),
            'avg_score': statistics.mean(sentence_scores),
            'total_score': sum(sentence_scores)
        }

    def sliding_window_analysis(self, text, window_size=3):
        sentences = self.split_into_sentences(text)
        if len(sentences) < window_size:
            return {'most_positive': {'text': 'N/A', 'score': 0},
                    'most_negative': {'text': 'N/A', 'score': 0}}

        windows = []
        for i in range(len(sentences) - window_size + 1):
            window_sentences = sentences[i:i+window_size]
            window_text = ' '.join(window_sentences)
            window_score = sum(self.get_sentence_score(s) for s in window_sentences)
            windows.append({'text': window_text, 'score': window_score})

        windows.sort(key=lambda x: x['score'])
        return {'most_negative': windows[0], 'most_positive': windows[-1]}

    def process_dataset(self, dataset_file_path):
        import re
        most_positive_review = {'text': '', 'score': -float('inf')}
        most_negative_review = {'text': '', 'score': float('inf')}
        total_reviews = 0

        try:
            with open(dataset_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Strip __label__X from the start
                    text = re.sub(r'^__label__\d+\s+', '', line)
                    total_reviews += 1
                    total_score = self.get_sentence_score(text)

                    if total_score > most_positive_review['score']:
                        most_positive_review = {'text': text, 'score': total_score}
                    if total_score < most_negative_review['score']:
                        most_negative_review = {'text': text, 'score': total_score}
        except Exception as e:
            return {'error': str(e)}

        return {
            'most_positive_review': most_positive_review,
            'most_negative_review': most_negative_review,
            'total_reviews_processed': total_reviews
        }

