"""
Test EdgarScreener
"""

import unittest

from baseurls import SEC_EDGAR
from tracker.screener import EdgarScreener


class EdgarScreenerTests(unittest.TestCase):
    """
    EdgarScreener Tests
    """

    def test_init(self):
        """
        Test Initialization
        """
        name = 'test_init'

        screener = EdgarScreener(name)
        self.assertIsNotNone(screener)
        self.assertEqual(name, screener.name)
        self.assertEqual(SEC_EDGAR, screener.url)

        # Test Filters init dict
        filters = ['q',
                   'dateRange',
                   'category',
                   'ciks',
                   'entityName',
                   'page',
                   'from',
                   'startdt',
                   'enddt',
                   'forms']
        self.assertEqual(list(screener.filters.keys()), filters)

    def test_build_url(self):
        """
        Test build_url() method
        """

        screener = EdgarScreener('test_build')

        # Manually Update the filters dict
        screener.filters = {
            'q': 'Annual Report',
            'dateRange': 'custom',
            'category': 'form-cat1',
            'ciks': ['0000320193'],
            'entityName': 'Apple Inc',
            'startdt': '2010-01-01',
            'enddt': '2020-12-31'
        }

        url_expected = r'https://www.sec.gov/edgar/search/#/q=Annual%2520Report&dateRange=custom&' \
                       r'category=form-cat1&ciks=0000320193&entityName=Apple%2520Inc&' \
                       r'startdt=2010-01-01&enddt=2020-12-31'

        self.assertEqual(url_expected, screener.build_url())

        # Test exact phrase search
        screener.filters['q'] = '\"Annual\" Report'

        url_expected = r'https://www.sec.gov/edgar/search/#/q=%2522Annual%2522%2520Report&' \
                       r'dateRange=custom&category=form-cat1&ciks=0000320193&' \
                       r'entityName=Apple%2520Inc&startdt=2010-01-01&enddt=2020-12-31'

        self.assertEqual(url_expected, screener.build_url())

    def test_filter_phrase(self):
        """
        Test filter_phrase() method
        """

        screener = EdgarScreener('test_filter_phrase')

        # Test Phrase Filter
        # Add phrase filter and check if filters dict updates
        phrase = 'Annual report'
        screener.filter_phrase(phrase)
        self.assertEqual(phrase, screener.filters['q'])

        # Test build_url
        url = r'https://www.sec.gov/edgar/search/#/q=Annual%2520report'
        self.assertEqual(url, screener.build_url())

        # Override phrase filter and check filter_phrase function returns old phrase
        new_phrase = 'Current report'
        self.assertEqual(phrase, screener.filter_phrase(new_phrase))
        self.assertEqual(new_phrase, screener.filters['q'])

        # Test build_url
        url = r'https://www.sec.gov/edgar/search/#/q=Current%2520report'
        self.assertEqual(url, screener.build_url())

        # Remove filter
        self.assertTrue(screener.remove_filter_phrase())
        self.assertIsNone(screener.filters['q'])

        # Try removing phrase filter, when already empty and verify function returns False
        self.assertFalse(screener.remove_filter_phrase())

        # Test build_url
        self.assertEqual(SEC_EDGAR, screener.build_url())

    def test_filter_name(self):
        """
        Test filter_name() method
        """

        screener = EdgarScreener('test_filter_name')

        # Test Name Filter
        name = 'AAPL'
        screener.filter_name(name)
        self.assertEqual(name, screener.filters['entityName'])

        # Test build_url
        url = r'https://www.sec.gov/edgar/search/#/entityName=AAPL'
        self.assertEqual(url, screener.build_url())

        # Override name filter and check filter_name function returns old name
        new_name = 'MSFT'
        self.assertEqual(name, screener.filter_name(new_name))
        self.assertEqual(new_name, screener.filters['entityName'])

        # Test build_url
        url = r'https://www.sec.gov/edgar/search/#/entityName=MSFT'
        self.assertEqual(url, screener.build_url())

        # Remove filter
        self.assertTrue(screener.remove_filter_name())
        self.assertIsNone(screener.filters['entityName'])

        # Try removing name filter, when already empty and verify function returns False
        self.assertFalse(screener.remove_filter_name())

        # Test build_url
        self.assertEqual(SEC_EDGAR, screener.build_url())

    def test_filter_ciks(self):
        """
        Test filter_ciks() method
        """

        screener = EdgarScreener('test_filter_ciks')

        # Test CIK Filter
        cik = '0000320193'
        screener.filter_ciks(cik)
        self.assertEqual([cik], screener.filters['ciks'])

        # Test build_url
        url = r'https://www.sec.gov/edgar/search/#/ciks=0000320193'
        self.assertEqual(url, screener.build_url())

        # Override ciks filter and check filter_ciks function returns old ciks
        cik_int = 320193
        self.assertEqual([cik], screener.filter_ciks(cik_int))
        self.assertEqual([str(cik_int).zfill(10)], screener.filters['ciks'])
        self.assertEqual(url, screener.build_url())

        # Redo with ciks list
        new_ciks = ['0000320193', 789019, '00001652044']
        new_url = r'https://www.sec.gov/edgar/search/#/' \
                  r'ciks=0000320193%252C0000789019%252C0001652044'
        self.assertEqual([str(cik_int).zfill(10)], screener.filter_ciks(new_ciks))
        self.assertEqual(['0000320193', '0000789019', '0001652044'], screener.filters['ciks'])
        self.assertEqual(new_url, screener.build_url())

        # Remove filter
        self.assertTrue(screener.remove_filter_ciks())
        self.assertEqual(SEC_EDGAR, screener.build_url())

        # Try removing filter even when empty
        self.assertFalse(screener.remove_filter_ciks())
        self.assertEqual(SEC_EDGAR, screener.build_url())

    def test_filter_filing_types(self):
        """
        Test filter_filing_types() method
        """

        screener = EdgarScreener('test_filter_filing_types')

        # Test Form Filter
        form_types = 4
        screener.filter_filing_types(form_types)
        self.assertEqual('4', screener.filters['forms'])
        self.assertEqual('custom', screener.filters['category'])

        # Test build_url
        url = r'https://www.sec.gov/edgar/search/#/category=custom&forms=4'
        self.assertEqual(url, screener.build_url())

        # Override forms filter and check filter_ciks function returns old filters
        new_form_types = [3, 4, 5, '10-K', '10-q']
        self.assertEqual('4', screener.filter_filing_types(new_form_types))
        self.assertEqual('3,4,5,10-K,10-Q', screener.filters['forms'])
        self.assertEqual('custom', screener.filters['category'])

        # Test build_url
        url = r'https://www.sec.gov/edgar/search/#/' \
              r'category=custom&forms=3%252C4%252C5%252C10-K%252C10-Q'
        self.assertEqual(url, screener.build_url())

        # Check if both forms and category update when forms filter is removed
        self.assertTrue(screener.remove_filter_filing_types())
        self.assertIsNone(screener.filters['forms'])
        self.assertIsNone(screener.filters['category'])

        # Try removing filing types filter, when already empty and verify function return False
        self.assertFalse(screener.remove_filter_filing_types())

        # Test build_url
        self.assertEqual(SEC_EDGAR, screener.build_url())


if __name__ == '__main__':
    unittest.main()
