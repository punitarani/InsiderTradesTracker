import unittest
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from baseurls import SEC_LATEST_FILINGS
from tracker.parser import SECParser, SECFilingsParser, SECFilingParser, ResponseError
from tracker.parser.webpage_parser import WebpageParser


class BasicParserTests(unittest.TestCase):
    def test_google(self):
        url = 'https://www.google.com/'

        parser = WebpageParser('Google', url)
        self.assertEqual(parser.name, 'Google')
        self.assertEqual(parser.url, url)
        self.assertIsNone(parser.response)
        self.assertIsNone(parser.response_dt)
        self.assertIsNone(parser.webpage)
        self.assertIsNone(parser.content_type)
        self.assertIsNone(parser.soup)

        # Test __repr__()
        self.assertEqual(str(parser), f'Google Parser for {url}.\n')

        # Test get_webpage()
        webpage = parser.get_webpage()
        self.assertIsNotNone(webpage)
        self.assertAlmostEqual(parser.response_dt, datetime.now(), delta=timedelta(seconds=10))

        # Test get_soup()
        soup = parser.get_soup()
        self.assertIsNotNone(soup)

    def test_sec_gov(self):
        parser = SECFilingsParser('SEC')
        self.assertEqual(parser.name, 'SEC')
        self.assertEqual(parser.url, SEC_LATEST_FILINGS)

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

    def test_errors(self):
        error = ResponseError('Test Error', 0)
        self.assertEqual(error.message, 'Test Error')
        self.assertEqual(error.status_code, 0)


class SECParserTests(unittest.TestCase):
    def test_init(self):
        parser_name = 'SEC'
        parser_url = 'https://www.sec.gov/'
        parser = SECParser(parser_name, parser_url)
        self.assertIsNotNone(parser)
        self.assertEqual(parser.name, parser_name)
        self.assertEqual(parser.url, parser_url)
        self.assertIsNone(parser.response)
        self.assertIsNone(parser.response_dt)
        self.assertIsNone(parser.webpage)
        self.assertIsNone(parser.content_type)
        self.assertIsNone(parser.soup)

        # Test set_url()
        new_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
        parser.set_url(new_url)
        self.assertEqual(parser.url, new_url)

    def test_get_webpage(self):
        parser = SECParser('SEC', 'https://www.sec.gov/')
        webpage = parser.get_webpage()
        self.assertEqual(parser.response.status_code, 200)
        self.assertIsNotNone(webpage)
        self.assertAlmostEqual(parser.response_dt, datetime.now(), delta=timedelta(seconds=10))
        self.assertIn('html', parser.content_type)

        # Parse function is abstract, so should be None
        self.assertIsNone(parser.parse())
        self.assertIsNone(parser.soup)


class SECLatestFilingsParserTests(unittest.TestCase):
    def test_parse(self):
        filings = SECFilingsParser('Filings')
        self.assertTrue(isinstance(filings.filings, pd.DataFrame))
        self.assertEqual(filings.filings.shape, (0, 0))

        filings.parse()
        self.assertGreater(filings.filings.shape[0], 0)
        self.assertGreater(filings.filings.shape[1], 0)


class SECFilingParserTests(unittest.TestCase):
    def test_init(self):
        parser_name = 'FilingParser'
        parser_url = 'https://www.sec.gov/Archives/edgar/data/' \
                     '0000320193/000032019321000071/0000320193-21-000071-index.html'
        parser = SECFilingParser(parser_name, parser_url)
        self.assertIsNotNone(parser)
        self.assertEqual(parser.name, parser_name)
        self.assertEqual(parser.url, parser_url)

        # Test get_webpage()
        webpage = parser.get_webpage()
        self.assertIsNotNone(webpage)

        # Test get_soup()
        soup = parser.get_soup()
        self.assertIsNotNone(soup)

    def test_parse(self):
        parser_name = 'FilingParser'
        parser_url = 'https://www.sec.gov/Archives/edgar/data/' \
                     '0000320193/000032019321000071/0000320193-21-000071-index.html'
        parser = SECFilingParser(parser_name, parser_url)

        # Test parse()
        parser.parse()
        self.assertIsNotNone(parser.data)
        self.assertEqual(parser.data.shape, (3, 6))
        self.assertEqual(parser.data.columns.tolist(), ['Seq', 'Description', 'Document', 'Type', 'Size', 'Link'])

        # Verify Accuracy
        # Test row 1
        self.assertEqual(parser.data.iloc[0, 0], 1)
        self.assertEqual(parser.data.iloc[0, 1], 'FORM 4')
        self.assertEqual(parser.data.iloc[0, 2], 'wf-form4_162984422696515.html')
        self.assertEqual(parser.data.iloc[0, 3], 4)

        # Test row 2
        self.assertEqual(parser.data.iloc[1, 0], 1)
        self.assertEqual(parser.data.iloc[1, 1], 'FORM 4')
        self.assertEqual(parser.data.iloc[1, 2], 'wf-form4_162984422696515.xml')
        self.assertEqual(parser.data.iloc[1, 3], 4)
        self.assertEqual(parser.data.iloc[1, 4], 3975)

        # Test row 3
        self.assertTrue(np.isnan(parser.data.iloc[2, 0]))
        self.assertEqual(parser.data.iloc[2, 1], 'Complete submission text file')
        self.assertEqual(parser.data.iloc[2, 2], '0000320193-21-000071.txt')
        self.assertEqual(parser.data.iloc[2, 4], 5473)

    def test_get_doc_url(self):
        parser_name = 'FilingParser'
        parser_url = 'https://www.sec.gov/Archives/edgar/data/' \
                     '0000320193/000032019321000071/0000320193-21-000071-index.html'
        parser = SECFilingParser(parser_name, parser_url)

        # Test get_doc_url()
        xml_url = parser.get_document_url(prefer_xml=True)
        html_url = parser.get_document_url(prefer_xml=False)
        correct_html_url = 'https://www.sec.gov/Archives/edgar/data/320193/000032019321000071/' \
                           'xslF345X03/wf-form4_162984422696515.xml'
        correct_xml_url = 'https://www.sec.gov/Archives/edgar/data/320193/000032019321000071/' \
                          'wf-form4_162984422696515.xml'
        self.assertEqual(xml_url, correct_xml_url)
        self.assertEqual(html_url, correct_html_url)

    def test_get_doc_url_2(self):
        # Test with different url that has no xml
        parser_url = 'https://www.sec.gov/Archives/edgar/data/' \
                     '0000320193/000119312516439878/0001193125-16-439878-index.html'
        parser = SECFilingParser('FilingParser', parser_url)

        # Test get_doc_url()
        xml_url = parser.get_document_url(prefer_xml=True)
        html_url = parser.get_document_url(prefer_xml=False)
        correct_html_url = 'https://www.sec.gov/Archives/edgar/data/320193/000119312516439878/d66145d10q.htm'
        correct_xml_url = 'https://www.sec.gov/Archives/edgar/data/320193/000119312516439878/d66145d10q.htm'
        self.assertEqual(xml_url, correct_xml_url)
        self.assertEqual(html_url, correct_html_url)


if __name__ == '__main__':
    unittest.main()
