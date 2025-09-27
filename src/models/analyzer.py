import re

class SentimentAnalyzer:
    def __init__(self, afinn_path='data/AFINN-en-165.txt'):
        # Load the AFINN sentiment dictionary once when we create the object.
        # This way we don't read the file every time we score some text—faster!
        self.afinn_dict = self._load_afinn_dict(afinn_path)

    def _load_afinn_dict(self, filepath):
        """
        Read the AFINN file and build a dictionary of word -> sentiment score.
        Each line in the file is like: 'happy\t3'
        Using a dictionary makes lookups super fast (O(1) per word).
        """
        afinn = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word, score = line.strip().split('\t')
                afinn[word] = int(score)  # Make sure score is an integer
        return afinn

    def _tokenize(self, text: str):
        """
        Break the text into words.
        - Uses regex to find words (letters, numbers, underscores)
        - Converts everything to lowercase so dictionary matches are consistent
        """
        return re.findall(r'\b\w+\b', text.lower())

    def score(self, text: str) -> float:
        """
        Calculate the sentiment score of a piece of text.
        - Tokenize the text
        - Sum the sentiment score for each word (0 if the word isn't in the dictionary)
        - Returns 0 if text is empty
        """
        if not text:
            return 0

        tokens = self._tokenize(text)

        # Using a generator expression so we don't create a list in memory
        # Each lookup is O(1), so total time is linear with number of words
        return sum(self.afinn_dict.get(word, 0) for word in tokens)
