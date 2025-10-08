
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))


import unittest
from analysis.segmentation import segment_text

class TestSegmentation(unittest.TestCase):
    def setUp(self):
        self.dictionary = {"bitcoin", "loss", "profit"}

    def test_valid_segmentation(self):
        text = "bitcoinlossprofit"
        result = segment_text(text, self.dictionary)
        self.assertEqual(result, ["bitcoin", "loss", "profit"])

    def test_invalid_segmentation(self):
        text = "abcdxyz"
        result = segment_text(text, self.dictionary)
        self.assertEqual(result, [])

    def test_empty_input(self):
        result = segment_text("", self.dictionary)
        self.assertEqual(result, [])

    def test_mixed_case_input(self):
        text = "BitcoinLossProfit"
        result = segment_text(text, self.dictionary)
        self.assertEqual(result, ["bitcoin", "loss", "profit"])

    def test_leading_spaces(self):
        text = "   bitcoinlossprofit   "
        result = segment_text(text, self.dictionary)
        self.assertEqual(result, ["bitcoin", "loss", "profit"])

if __name__ == "__main__":
    unittest.main()
