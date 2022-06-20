import unittest

import pandas as pd

from baseurls import SEC_EDGAR
from tracker.parser import EdgarParser


class TestEdgarParser(unittest.TestCase):
    def test_init(self):
        name = 'test'
        filters = {'category': 'custom', 'forms': ['4']}

        parser = EdgarParser(name, filters)

        # Check Init Variables
        self.assertEqual(name, parser.name)
        self.assertEqual(filters, parser.filters)

        # Verify irrelevant inherited attrs and methods function correctly
        self.assertFalse(hasattr(EdgarParser, 'url'))
        self.assertIsInstance(parser.set_url(), AttributeError)

    def test_webpage_parse(self):
        parser = EdgarParser('test_parse', filters={'category': 'custom', 'forms': ['4']})

        # Get Webpage
        self.assertIsInstance(parser.get_webpage(), dict)

        # Parse
        self.assertIsInstance(parser.parse(), pd.DataFrame)
        self.assertEqual((100, 6), parser.results.shape)
        self.assertEqual(['index', 'type', 'id', 'score', 'source', 'sort'], parser.results.columns.tolist())


if __name__ == '__main__':
    unittest.main()
