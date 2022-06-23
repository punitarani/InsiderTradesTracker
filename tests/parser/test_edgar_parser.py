"""
Test EdgarParser
"""

import unittest

import pandas as pd

from tracker.parser import EdgarParser


class TestEdgarParser(unittest.TestCase):
    """
    Test EdgarParser
    """

    def test_init(self):
        """
        Test Initialization
        """

        name = 'test'
        filters = {'category': 'custom', 'forms': ['4']}

        parser = EdgarParser(name, filters)

        # Check Init Variables
        self.assertEqual(name, parser.name)
        self.assertEqual(filters, parser.filters)
        self.assertIsNone(parser.results)
        self.assertIsNone(parser.results_count)
        self.assertEqual(0, parser.results_to)

        # Verify irrelevant inherited attrs and methods function correctly
        self.assertFalse(hasattr(EdgarParser, 'url'))
        self.assertIsInstance(parser.set_url(), AttributeError)

    def test_webpage_parse(self):
        """
        Test getWebpage() and parse() methods
        """

        parser = EdgarParser('test_parse', filters={'category': 'custom', 'forms': ['4']})

        # Get Webpage
        self.assertIsInstance(parser.get_webpage(), dict)

        # Parse
        self.assertIsInstance(parser.parse(), pd.DataFrame)
        self.assertEqual((100, 6), parser.results.shape)
        self.assertEqual(['index', 'type', 'id', 'score', 'source', 'sort'],
                         parser.results.columns.tolist())
        self.assertEqual(10000, parser.results_count)
        self.assertEqual(100, parser.results_to)


if __name__ == '__main__':
    unittest.main()
