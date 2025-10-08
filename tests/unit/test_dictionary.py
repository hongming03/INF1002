import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

import unittest
from src.analysis.segmentation import get_full_dictionary

class TestDictionary(unittest.TestCase):
    def test_contains_crypto_terms(self):
        dictionary = get_full_dictionary()
        self.assertIn("bitcoin", dictionary)
        self.assertIn("blockchain", dictionary)

    def test_dictionary_not_empty(self):
        dictionary = get_full_dictionary()
        self.assertTrue(len(dictionary) > 0)

    def test_dictionary_type(self):
        dictionary = get_full_dictionary()
        self.assertIsInstance(dictionary, set)

    def test_common_english_word_exists(self):
        dictionary = get_full_dictionary()
        # if nltk loaded successfully
        self.assertIn("the", dictionary)

if __name__ == "__main__":
    unittest.main()
