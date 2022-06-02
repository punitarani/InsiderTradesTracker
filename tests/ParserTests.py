import unittest
from src.parsers.WebpageParser import WebpageParser
from src.parsers.SECFilingsParser import SECFilingsParser


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
        url = 'https://www.sec.gov/'

        parser = SECFilingsParser('SEC', url)
        self.assertEqual(parser.name, 'SEC')
        self.assertEqual(parser.url, url)

        webpage = parser.get_webpage()
        self.assertIsNotNone(webpage)

        soup = parser.get_soup()
        self.assertIsNotNone(soup)
        self.assertIn('SEC.gov', soup.title.string)

    def test_sec_filings(self):
        # 10 Latest Filings
        url = 'https://www.sec.gov/cgi-bin/browse-edgar?count=10&action=getcurrent'

        parser = SECFilingsParser('SEC Latest Filings', url)
        self.assertEqual(parser.name, 'SEC Latest Filings')
        self.assertEqual(parser.url, url)

        webpage = parser.get_webpage()
        self.assertIsNotNone(webpage)

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


if __name__ == '__main__':
    unittest.main()
