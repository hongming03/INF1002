# src/analyzer.py

import re
import statistics
import os
import tempfile

class SentimentAnalyzer:
    """
    A modular class to handle all sentiment analysis logic.
    """
    def __init__(self, afinn_file_path):
        """Initializes the analyzer by loading the AFINN dictionary from a file path."""
        self.afinn_dict = {}
        self.load_afinn_dict_from_file(afinn_file_path)
    
    def load_afinn_dict_from_file(self, afinn_file_path):
        """Loads the AFINN dictionary from a specified file."""
        try:
            with open(afinn_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '\t' in line:
                        word, score = line.split('\t')
                        self.afinn_dict[word.lower()] = int(score)
            print(f"Loaded {len(self.afinn_dict)} words from AFINN dictionary.")
        except FileNotFoundError:
            print(f"Error: AFINN file not found at path: {afinn_file_path}")
            self.afinn_dict = {}
        except Exception as e:
            print(f"Error loading AFINN dictionary from file: {e}")
            self.afinn_dict = {}

    def clean_text(self, text):
        """
        Cleans and tokenizes text by removing punctuation and converting to lowercase.
        """
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text.split()
    
    def get_sentence_score(self, sentence):
        """
        Calculates the sentiment score for a single sentence based on the dictionary.
        """
        words = self.clean_text(sentence)
        scores = [self.afinn_dict.get(word, 0) for word in words]
        return sum(scores) if scores else 0
    
    def split_into_sentences(self, text):
        """
        Splits a block of text into individual sentences.
        """
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def analyze_text(self, text):
        """
        Performs a full sentiment analysis on the entire text.
        """
        sentences = self.split_into_sentences(text)
        
        if not sentences:
            return {
                'sentences': [],
                'sentence_scores': [],
                'most_positive_sentence': None,
                'most_negative_sentence': None,
                'avg_score': 0,
                'total_score': 0
            }
        
        sentence_scores = [self.get_sentence_score(s) for s in sentences]
        
        # Find the most positive and most negative sentences and their scores
        most_positive_sentence = None
        most_negative_sentence = None
        if sentences:
            max_score_idx = sentence_scores.index(max(sentence_scores))
            min_score_idx = sentence_scores.index(min(sentence_scores))
            most_positive_sentence = (sentences[max_score_idx], sentence_scores[max_score_idx])
            most_negative_sentence = (sentences[min_score_idx], sentence_scores[min_score_idx])
            
        return {
            'sentences': sentences,
            'sentence_scores': sentence_scores,
            'most_positive_sentence': most_positive_sentence,
            'most_negative_sentence': most_negative_sentence,
            'avg_score': statistics.mean(sentence_scores) if sentence_scores else 0,
            'total_score': sum(sentence_scores)
        }
    
    def sliding_window_analysis(self, text, window_size=3):
        """
        Performs sliding window analysis to find the most positive/negative segments.
        """
        sentences = self.split_into_sentences(text)
        if len(sentences) < window_size:
            return {
                'most_positive': {'text': 'N/A', 'score': 0},
                'most_negative': {'text': 'N/A', 'score': 0}
            }
        
        windows = []
        for i in range(len(sentences) - window_size + 1):
            window_sentences = sentences[i:i + window_size]
            window_text = ' '.join(window_sentences)
            window_score = sum(self.get_sentence_score(s) for s in window_sentences)
            
            windows.append({
                'text': window_text,
                'score': window_score
            })
        
        windows.sort(key=lambda x: x['score'])
        
        return {
            'most_negative': windows[0] if windows else None,
            'most_positive': windows[-1] if windows else None
        }
    
    def process_dataset(self, dataset_file_path):
        """
        Processes a dataset file to find the most positive and negative reviews.
        Assumes each line is a review.
        """
        most_positive_review = {'text': '', 'score': -float('inf')}
        most_negative_review = {'text': '', 'score': float('inf')}
        total_reviews = 0

        try:
            with open(dataset_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(' ', 1)
                    if len(parts) < 2:
                        continue
                        
                    text = parts[1]
                    total_reviews += 1
                    analysis = self.analyze_text(text)
                    total_score = analysis['total_score']
                    
                    if total_score > most_positive_review['score']:
                        most_positive_review['score'] = total_score
                        most_positive_review['text'] = text
                    
                    if total_score < most_negative_review['score']:
                        most_negative_review['score'] = total_score
                        most_negative_review['text'] = text

        except Exception as e:
            print(f"Error processing dataset: {e}")
            return {'error': str(e)}

        return {
            'most_positive_review': most_positive_review,
            'most_negative_review': most_negative_review,
            'total_reviews_processed': total_reviews
        }
