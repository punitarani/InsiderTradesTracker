import unittest

from tracker.manage import LatestInsiderTrades


class TestBasicInsiderTrades(unittest.TestCase):
    def test_init(self):
        manager = LatestInsiderTrades()
        self.assertIsNotNone(manager)
        self.assertEqual(manager.screener.name, manager.screener_name)

    def test_filings(self):
        manager = LatestInsiderTrades()
        filings = manager.get_latest_filings()
        self.assertIsNotNone(filings)
        self.assertGreaterEqual(filings.shape, (1, 4))
        self.assertEqual(filings.columns.tolist(), ['form_type', 'title', 'date_time', 'link'])

    def test_parse(self):
        manager = LatestInsiderTrades()
        filings = manager.get_latest_filings()
        parsed = manager.parse_filings(filings.head(5))

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.shape, (5, 4))
        self.assertEqual(parsed.columns.tolist(), ['issuer', 'owner', 'non_derivative', 'derivative'])


if __name__ == '__main__':
    unittest.main()
