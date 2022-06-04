import unittest

import pandas as pd

from src.parsers.sec_filings_parser import SECFilingsParser, SEC_LATEST_FILINGS_URL
from src.parsers.webpage_parser import WebpageParser


class BasicParserTests(unittest.TestCase):
    def test_google(self):
        url = 'https://www.google.com/'

        parser = WebpageParser('Google', url)
        self.assertEqual(parser.name, 'Google')
        self.assertEqual(parser.url, url)

        webpage = parser.get_webpage()
        self.assertIsNotNone(webpage)

        soup = parser.get_soup()
        self.assertIsNotNone(soup)

    def test_sec_gov(self):
        parser = SECFilingsParser('SEC')
        self.assertEqual(parser.name, 'SEC')
        self.assertEqual(parser.url, SEC_LATEST_FILINGS_URL)

        # Test set_url()
        url = 'https://www.sec.gov/'
        parser.set_url(url)
        self.assertEqual(parser.url, url)

        # Test get_webpage()
        webpage = parser.get_webpage()
        self.assertIsNotNone(webpage)

        # Test get_soup()
        soup = parser.get_soup()
        self.assertIsNotNone(soup)
        self.assertIn('SEC.gov', soup.title.string)

    def test_sec_filings(self):
        # 10 Latest Filings
        url = 'https://www.sec.gov/cgi-bin/browse-edgar?count=10&action=getcurrent'

        parser = SECFilingsParser('SEC Latest Filings', url)
        self.assertEqual(parser.name, 'SEC Latest Filings')
        self.assertEqual(parser.url, url)

        # Test get_webpage()
        webpage = parser.get_webpage()
        self.assertIsNotNone(webpage)

        # Test get_soup()
        soup = parser.get_soup()
        self.assertIsNotNone(soup)

        # Initialize list of filing urls
        html_urls = list()

        # Get list of HTML links with '/Archives/edgar/data/' in href.
        for link in soup.find_all('a'):
            if '/Archives/edgar/data/' in link.get('href') and 'html' in link.text:
                html_urls.append('https://www.sec.gov' + link.get('href'))

        # Check if there are 10 filings
        self.assertEqual(len(html_urls), 10)


class SECFilingsParserTests(unittest.TestCase):
    def test_parse(self):
        filings = SECFilingsParser('Filings')
        self.assertTrue(isinstance(filings.filings, pd.DataFrame))
        self.assertEqual(filings.filings.shape, (0, 0))

        filings.parse()
        self.assertGreater(filings.filings.shape[0], 0)
        self.assertGreater(filings.filings.shape[1], 0)


if __name__ == '__main__':
    unittest.main()
