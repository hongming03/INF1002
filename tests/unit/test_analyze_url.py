import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

import unittest
from unittest.mock import patch
from analysis.analyze_url import handle_analyze_url


class TestHandleAnalyzeUrl(unittest.TestCase):
    def setUp(self):
        # Mock out render_template to skip Flask HTML rendering
        patcher = patch("analysis.analyze_url.render_template", return_value="OK")
        self.mock_render = patcher.start()
        self.addCleanup(patcher.stop)

    def test_empty_input(self):
        result = handle_analyze_url("", False)
        self.assertEqual(result, "OK")

    def test_invalid_url_format(self):
        result = handle_analyze_url("htt://badurl", False)
        self.assertEqual(result, "OK")

    def test_plain_text_input(self):
        result = handle_analyze_url("Bitcoin is great but volatile.", False)
        self.assertEqual(result, "OK")

    def test_force_segment(self):
        result = handle_analyze_url("bitcoinlossprofit", True)
        self.assertEqual(result, "OK")


if __name__ == "__main__":
    unittest.main()
