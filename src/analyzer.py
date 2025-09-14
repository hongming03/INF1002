import re

class SentimentAnalyzer:
    def __init__(self, afinn_path='data/AFINN-en-165.txt'):
        # Loads sentiment dictionary once during initialization.
        # Avoids repeated file I/O and ensures fast access during scoring.
        self.afinn_dict = self._load_afinn_dict(afinn_path)

    def _load_afinn_dict(self, filepath):
        """
        Loads the AFINN sentiment dictionary from a text file.
        Each line contains a word and its sentiment score separated by a tab.
        Uses a dictionary for constant-time lookups (O(1) per word).
        """
        afinn = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word, score = line.strip().split('\t')
                afinn[word] = int(score)  # ✅ Integer conversion for faster arithmetic
        return afinn

    def _tokenize(self, text: str):
        """
        Tokenizes input text into lowercase words using regex.
        Regex is fast and avoids external dependencies like nltk.
        Lowercasing ensures consistent dictionary matching.
        """
        return re.findall(r'\b\w+\b', text.lower())

    def score(self, text: str) -> float:
        """
        Computes the sentiment score of the input text.
        Tokenizes the text and sums sentiment scores using dictionary lookups.
        Ignores unknown words efficiently using dict.get(word, 0).
        Generator expression avoids creating intermediate lists—memory efficient.
        """
        if not text:
            return 0

        tokens = self._tokenize(text)

        # Each lookup is O(1); total time is linear with respect to token count.
        return sum(self.afinn_dict.get(word, 0) for word in tokens)
