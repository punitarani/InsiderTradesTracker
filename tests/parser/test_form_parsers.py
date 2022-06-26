"""
Test FormParsers
"""

import unittest

import numpy as np

from tracker.parser import Form4Parser
from tracker.parser import form4_transaction_codes


class Form4Tests(unittest.TestCase):
    """
    Test Form4Parser
    """

    def test_form4_init(self):
        """
        Test Initialization
        """

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
        """
        Test parse() method
        """

        url = "https://www.sec.gov/Archives/edgar/data/19617/000122520822005164/doc4.xml"
        """
        Document Stats:
        - Document Type: 4
        - Document Date: 2022-03-25
        - 7 Non Derivative Transactions
        - 1 Derivative Transaction
        - 7 Footnotes
        - File Complexity: Multiple missing fields, different codes and descriptions.
        """

        parser = Form4Parser("Dimon", url)
        parser.parse()

        self.assertEqual((3, 1), parser.issuer_table.shape)
        self.assertEqual((11, 1), parser.owner_table.shape)
        self.assertEqual((7, 15), parser.non_derivative_table.shape)
        self.assertEqual((1, 16), parser.derivative_table.shape)
        self.assertEqual(7, len(parser.footnotes))

    def test_parse_accuracy(self):
        """
        Test parse() method accuracy
        """

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
                ['Common Stock', '2022-03-25', np.nan, '4', 'F', '0', np.nan, '220486.0522',
                 '141.9900', 'D', '1166561.0000', 'D', np.nan, np.nan, np.nan],
                ['Common Stock', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
                 np.nan, '4348004.0000', 'I', np.nan, np.nan, 'By GRATs']
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
        expected_values = ['Performance Share Units', np.nan, '2022-03-25', '4', 'M', '0', np.nan,
                           '398708.0522', '0.0000', 'D', np.nan, np.nan, 'Common Stock',
                           '398708.0522', '0.0000', 'D']

        for j, col in enumerate(parser.derivative_table.columns):
            data_point = parser.derivative_table.loc[1, col]

            # Try-Except to handle NaN values
            try:
                self.assertEqual(np.isnan(data_point), np.isnan(expected_values[j]))
            except TypeError:
                self.assertEqual(data_point, expected_values[j])

        # Test Footnotes
        expected_footnotes = {
            'F1': "These shares represent JPMC common stock acquired on March 25, 2022 upon "
                  "settlement of a Performance Share Unit (PSU) award granted on January 15, 2019 "
                  "for the three-year performance period ended December 31, 2021 (as previously "
                  "disclosed on a Form 4 filed on March 17, 2022), and must be held for an "
                  "additional two-year period, for a total combined vesting and holding period of "
                  "five years from the date of grant.",
            'F2': "Each PSU represents a contingent right to receive one share of JPMC common stock"
                  " upon vesting based on the attainment of performance goals.",
            'F3': "Balance reflects a) 310,028 shares transferred from a Grantor Retained Annuity "
                  "Trust (GRAT) to the Grantor on January 18, 2022; b) 141,528 shares transferred "
                  "from a GRAT to the Grantor on January 18, 2022. These transfers are exempt from "
                  "Section 16 pursuant to Rule 16a-13.",
            'F4': "Balance reflects 29,034 shares transferred from a Grantor Retained Annuity Trust"
                  " to the Grantor's Family Trusts on January 19, 2022. This transfer is exempt "
                  "from Section 16 pursuant to Rule 16a-13.",
            'F5': "Balance reflects a) 310,028 shares transferred from a Grantor Retained Annuity "
                  "Trust (GRAT) to the Grantor on January 18, 2022; b) 141,528 shares transferred "
                  "from a GRAT to the Grantor on January 18, 2022; c) 29,034 shares transferred "
                  "from GRAT to the Grantor's Family Trust on January 19, 2022. These transfers are"
                  " exempt from Section 16 pursuant to Rule 16a-13.",
            'F6': "Reporting person disclaims beneficial ownership of such shares except to the "
                  "extent of any pecuniary interest.",
            'F7': "Represents PSUs earned (including reinvested dividend equivalents) based on the "
                  "Firm's attainment of pre-established performance goals for the three-year "
                  "performance period ended December 31, 2021, as provided under the terms of a PSU"
                  " award granted on January 15, 2019, and as previously reported on a Form 4 filed"
                  " on March 17, 2022. The PSUs settled in shares of common stock on March 25, "
                  "2022. Shares delivered, after applicable tax withholding, must be held for an "
                  "additional two-year period, for a total combined vesting and holding period of "
                  "five years from the date of grant.",
        }

        self.assertEqual(expected_footnotes.keys(), parser.footnotes.keys())

        # Iterate through all footnotes
        for footnote_id, footnote_text in parser.footnotes.items():
            self.assertEqual(expected_footnotes[footnote_id], footnote_text)

    def test_transaction_codes(self):
        """
        Test transaction_codes dict
        """

        transaction_codes = form4_transaction_codes
        self.assertEqual(len(transaction_codes.keys()), 20)

        self.assertEqual(form4_transaction_codes['G'], "Bona fide gift.")
        self.assertEqual(form4_transaction_codes['L'], "Small acquisition under Rule 16a-6.")

        try:
            y_code = form4_transaction_codes['Y']
            self.fail(f"'Y' should not be in the transaction codes. Got {y_code}.\n")
        except KeyError:
            pass


if __name__ == '__main__':
    unittest.main()
