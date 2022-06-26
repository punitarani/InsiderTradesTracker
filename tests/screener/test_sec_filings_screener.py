"""
Test SECFilingsScreener
"""

import unittest

import pandas.testing as pdt
from numpy.random import randint

from baseurls import SEC_LATEST_FILINGS
from tracker.screener import SECFilingsScreener


class SECFilingsScreenerTests(unittest.TestCase):
    """
    SECFilingsScreener Tests
    """

    def test_init(self):
        """
        Test Initialization
        """

        screener_name = "form_4_screener"
        screener = SECFilingsScreener(screener_name)
        self.assertIsNotNone(screener)

        self.assertEqual(screener.name, screener_name)
        self.assertEqual(screener.base_url, SEC_LATEST_FILINGS)
        self.assertIsNone(screener.company)
        self.assertIsNone(screener.cik)
        self.assertIsNone(screener.form)
        self.assertIsNone(screener.owner)
        self.assertEqual(screener.count, 100)

        self.assertNotEqual(screener.url, SEC_LATEST_FILINGS)
        self.assertNotEqual(screener.get_url(), SEC_LATEST_FILINGS)
        self.assertTrue(screener.filings.empty)

        self.assertIsNotNone(screener.get_filings())
        self.assertGreaterEqual((100, 4), screener.get_filings().shape)
        self.assertEqual(["form_type", "title", "date_time", "link"],
                         screener.get_filings().columns.tolist())

    def test_set_count(self):
        """
        Test set_entries_count() method
        """

        screener = SECFilingsScreener("screener")
        self.assertEqual(screener.count, 100)
        self.assertEqual(screener.set_entries_count(200), 100)
        self.assertEqual(screener.set_entries_count(99), 80)
        self.assertEqual(screener.set_entries_count(50), 40)
        self.assertEqual(screener.set_entries_count(30), 20)
        self.assertEqual(screener.set_entries_count(11), 10)
        self.assertEqual(screener.set_entries_count(0), 10)
        self.assertEqual(screener.set_entries_count(-10), 10)

    def test_get_filings(self):
        """
        Test get_filings()
        """
        screener_name = "form_4_screener"
        screener = SECFilingsScreener(screener_name, form='4')

        # Test endswith('(Reporting)')
        # Get filtered filings
        filings = screener.get_filings(filter_str="(Reporting)", filter_condition="endswith")
        # Get all (unfiltered) filings
        all_filings = screener.filings
        # Verify filtering works
        self.assertEqual(all_filings[all_filings["title"].str.endswith("(Reporting)")].shape,
                         filings.shape)

        # Test endswith('(Issuer)')
        filings = screener.get_filings(filter_str="(Issuer)", filter_condition="endswith")
        all_filings = screener.filings
        self.assertEqual(all_filings[all_filings["title"].str.endswith("(Issuer)")].shape,
                         filings.shape)

        # Test contains('(Reporting)')
        filings = screener.get_filings(filter_str="(Reporting)", filter_condition="contains")
        all_filings = screener.filings
        self.assertEqual(all_filings[all_filings["title"].str.contains("(Reporting)")].shape,
                         filings.shape)

        # Test contains('(Issuer)')
        filings = screener.get_filings(filter_str="(Issuer)", filter_condition="contains")
        all_filings = screener.filings
        self.assertEqual(all_filings[all_filings["title"].str.contains("(Issuer)")].shape,
                         filings.shape)

    def test_filters(self):
        """
        Test filter_*() methods
        """

        screener_name = "form_4_screener"
        screener = SECFilingsScreener(screener_name)

        # No Filters
        self.assertFalse(screener.get_filings().empty)
        self.assertLessEqual(screener.get_filings('(Issuer)', 'endswith').shape, (100, 4))

        # Filter Form Type
        screener.filter_form("4")
        self.assertEqual("4", screener.form)
        self.assertLessEqual((1, 4),
                             screener.get_filings('(Reporting)', "endswith").shape)

        # Filter by owner
        # When no owner is included, there should be no form 4 filings
        screener.filter_owner(include=False)
        self.assertEqual(0, screener.get_filings(filter_str=None).shape[0])

        screener.filter_owner(include=True)
        self.assertEqual((100, 4), screener.get_filings(filter_str=None).shape)

        screener.filter_owner(only=True)
        self.assertEqual((100, 4), screener.get_filings(filter_str=None).shape)

        # Pick a random company
        _filings = screener.get_filings("(Issuer)", "endswith")
        random_company = _filings.iloc[randint(0, _filings.shape[0])]["title"]
        random_company = random_company.split(" - ")[-1].split(" (")[0]

        # Filter by Company
        screener.filter_company(random_company)
        print(random_company)
        self.assertEqual(random_company, screener.company)
        self.assertIn(random_company,
                      str(screener.get_filings('(Issuer)').iloc[0].loc["title"]))

        # Filter by CIK
        # JP Morgan Chase & Co. CIK: 0000019617
        # JP Morgan has been found to file frequently, so we will use their CIK.
        # There could be times when JP Morgan does not file daily, which can fail the test.
        jpm_cik = "0000019617"
        screener.filter_cik(jpm_cik)
        screener.filter_owner(include=False)
        screener.filter_form(None)
        screener.filter_company(None)

        self.assertEqual(jpm_cik, screener.cik)
        self.assertIn("JPMORGAN CHASE & CO",
                      str(screener.get_filings().iloc[0].loc["title"]))

    def test_get_filings_until(self):
        """
        Test get_filings_until() methods
        """

        screener = SECFilingsScreener("screener", form="4")

        # Get all the filings
        filings = screener.get_filings()
        self.assertGreater(filings.shape, (0, 4))

        # Pick a random filing
        random_index = randint(0, filings.shape[0])
        random_filing = filings.iloc[random_index]
        random_acc = filings.index[random_index]

        self.assertIsNotNone(random_acc)

        # Get all the filings until the random filing
        filings_until = screener.get_filings_until(random_acc)
        self.assertGreaterEqual(filings_until.shape[0], random_index)

        # Verify that random_acc is not in the filings
        pdt.assert_series_equal(filings_until.iloc[-1], random_filing)

        # Test max_count sets to 2000
        filings_until = screener.get_filings_until("", max_count=3000)
        self.assertLessEqual(filings_until.shape[0], 2000)


if __name__ == '__main__':
    unittest.main()
