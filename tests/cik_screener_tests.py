# CIK Screener Tests

import unittest

import pandas as pd

from tracker.screener.cik_screener import CIKScreener


class CIKScreenerTests(unittest.TestCase):
    def test_init(self):
        screener = CIKScreener()
        self.assertIsNotNone(screener)
        self.assertEqual(screener.lookup_df.shape, (0, 0))

    def test_lookup_df(self):
        screener = CIKScreener()

        # Test Get, Save, and Load Lookup DataFrame
        self.assertTrue(isinstance(screener._get_lookup_df_from_url(), pd.DataFrame))

        # Save df size to compare later
        df_size = screener.get_lookup_df().shape

        self.assertTrue(df_size[0] > 0)
        self.assertEqual(df_size[1], 2)

        self.assertTrue(screener._save_lookup_df_to_parquet())
        self.assertTrue(isinstance(screener._load_lookup_df_from_parquet(), pd.DataFrame))

        # Compare saved and loaded df
        self.assertEqual(screener.get_lookup_df().shape, df_size)

    def test_accuracy(self):
        screener = CIKScreener()

        apple_cik = "0000320193"
        apple_name = "APPLE INC."

        df = screener.filter_cik(apple_cik)
        self.assertTrue(df['company'].str.contains(apple_name).any())

        df = screener.filter_company("Apple Inc.")
        self.assertTrue(df['cik'].str.contains(apple_cik).any())


if __name__ == '__main__':
    unittest.main()
