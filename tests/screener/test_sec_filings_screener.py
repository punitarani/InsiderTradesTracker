import unittest

from baseurls import SEC_LATEST_FILINGS
from tracker.screener import SECFilingsScreener

import pandas.testing as pdt
import numpy as np


class BasicTests(unittest.TestCase):
    def test_init(self):
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
        self.assertLessEqual(screener.get_filings().shape, (100, 4))
        self.assertEqual(screener.get_filings().columns.tolist(), ["form_type", "title", "date_time", "link"])

    def test_set_count(self):
        screener = SECFilingsScreener("screener")
        self.assertEqual(screener.count, 100)
        self.assertEqual(screener.set_entries_count(200), 100)
        self.assertEqual(screener.set_entries_count(99), 80)
        self.assertEqual(screener.set_entries_count(50), 40)
        self.assertEqual(screener.set_entries_count(30), 20)
        self.assertEqual(screener.set_entries_count(11), 10)
        self.assertEqual(screener.set_entries_count(0), 10)
        self.assertEqual(screener.set_entries_count(-10), 10)

    def test_filters(self):
        screener_name = "form_4_screener"
        screener = SECFilingsScreener(screener_name)

        # No Filters
        self.assertFalse(screener.get_filings().empty)
        self.assertLessEqual(screener.get_filings().shape, (100, 4))

        # Filter Form Type
        screener.filter_form("4")
        self.assertEqual(screener.form, "4")
        self.assertGreaterEqual(screener.get_filings().shape, (1, 4))

        # Filter by owner
        # When no owner is included, there should be no form 4 filings
        screener.filter_owner(include=False)
        self.assertEqual(screener.get_filings().shape[0], 0)

        screener.filter_owner(include=True)
        self.assertGreaterEqual(screener.get_filings().shape, (1, 4))

        screener.filter_owner(only=True)
        self.assertGreaterEqual(screener.get_filings().shape, (1, 4))

        # Filter by Company
        # Pick a random company
        random_company = screener.get_filings().iloc[np.random.randint(0, screener.get_filings().shape[0])]["title"]
        random_company = random_company.split(" - ")[-1].split(" (")[0]
        screener.filter_company(random_company)
        self.assertEqual(screener.company, random_company)
        self.assertTrue(random_company in str(screener.get_filings().iloc[0].loc["title"]))

        # Filter by CIK
        # JP Morgan Chase & Co. CIK: 0000019617
        # JP Morgan has been found to file frequently, so we will use their CIK.
        # There could be times when JP Morgan does not file daily, which can fail the test.
        jpm_cik = "0000019617"
        screener.filter_cik(jpm_cik)
        screener.filter_owner(include=False)
        screener.filter_form(None)
        screener.filter_company(None)
        self.assertEqual(screener.cik, jpm_cik)
        self.assertTrue("JPMORGAN CHASE & CO" in str(screener.get_filings().iloc[0].loc["title"]))

    def test_get_filings_until(self):
        screener = SECFilingsScreener("screener", form="4")

        # Get all the filings
        filings = screener.get_filings()
        self.assertGreater(filings.shape, (0, 4))

        # Pick a random filing
        random_index = np.random.randint(0, filings.shape[0])
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
