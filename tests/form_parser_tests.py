import unittest

import numpy as np

from src.parsers.form_4 import Form4Parser


class Form4Tests(unittest.TestCase):
    def test_form4_init(self):
        url = "https://www.sec.gov/Archives/edgar/data/19617/000122520822005164/doc4.xml"
        parser = Form4Parser("Dimon", url)

        self.assertEqual(parser.name, "Dimon")
        self.assertEqual(parser.url, url)

        self.assertIsNone(parser.webpage)
        self.assertIsNone(parser.soup)

        self.assertEqual(parser.issuer_table.shape, (0, 0))
        self.assertEqual(parser.owner_table.shape, (0, 0))
        self.assertEqual(parser.non_derivative_table.shape, (0, 0))
        self.assertEqual(parser.derivative_table.shape, (0, 0))

        self.assertTrue(isinstance(parser.filings, AttributeError))

    def test_parse(self):
        url = "https://www.sec.gov/Archives/edgar/data/19617/000122520822005164/doc4.xml"
        """
        Document Stats:
        Document Type: 4
        Document Date: 2022-03-25
        7 Non Derivative Transactions
        1 Derivative Transaction
        File Complexity: Multiple missing fields, different codes and descriptions.
        """

        parser = Form4Parser("Dimon", url)
        parser.parse()

        self.assertEqual(parser.issuer_table.shape, (3, 1))
        self.assertEqual(parser.owner_table.shape, (11, 1))
        self.assertEqual(parser.non_derivative_table.shape, (7, 15))
        self.assertEqual(parser.derivative_table.shape, (1, 16))

    def test_parse_accuracy(self):
        url = "https://www.sec.gov/Archives/edgar/data/19617/000122520822005164/doc4.xml"
        parser = Form4Parser("Dimon", url)
        parser.parse()

        # Test All Contents of Issuer Table
        self.assertListEqual(parser.issuer_table.loc[:, 0].values.tolist(),
                             ['0000019617', 'JPMORGAN CHASE & CO', 'JPM'])

        # Test All Contents of Owner Table
        self.assertListEqual(parser.owner_table.loc[:, 0].values.tolist(), [
            '0001195345', 'DIMON JAMES', '383 MADISON AVENUE', np.nan, 'NEW YORK',
            'NY', '10179-0001', np.nan, '1', '1', 'Chairman & CEO'
        ])

        # Test rows 2 and 5 of Non-Derivative Table
        for i, row in enumerate([2, 5]):
            row_data = [
                ['Common Stock', '2022-03-25', np.nan, '4', 'F', '0', np.nan, '220486.0522', '141.9900', 'D',
                 '1166561.0000', 'D', np.nan, np.nan, np.nan],
                ['Common Stock', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
                 '4348004.0000', 'I', np.nan, np.nan, 'By GRATs']
            ]

            for j, col in enumerate(parser.non_derivative_table.columns):
                data_point = parser.non_derivative_table.loc[row, col]
                expected_value = row_data[i][j]

                # Try-Except to handle NaN values
                try:
                    self.assertEqual(np.isnan(data_point), np.isnan(expected_value))
                except TypeError:
                    self.assertEqual(data_point, expected_value)

        # Test row 1 of Derivative Table
        expected_values = ['Performance Share Units', np.nan, '2022-03-25', '4', 'M', '0', np.nan, '398708.0522',
                           '0.0000', 'D', np.nan, np.nan, 'Common Stock', '398708.0522', '0.0000', 'D']

        for j, col in enumerate(parser.derivative_table.columns):
            data_point = parser.derivative_table.loc[1, col]

            # Try-Except to handle NaN values
            try:
                self.assertEqual(np.isnan(data_point), np.isnan(expected_values[j]))
            except TypeError:
                self.assertEqual(data_point, expected_values[j])


if __name__ == '__main__':
    unittest.main()
