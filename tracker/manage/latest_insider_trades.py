# Latest Insider Trades Tracker Module

from pathlib import Path

import pandas as pd

from defs import DATA_DIR_PATH
from tracker.parsers import Form4Parser, SECFilingParser
from tracker.screener import SECFilingsScreener


class LatestInsiderTrades:
    """
    Get the latest insider trades.
    """

    def __init__(self):
        """
        LatestInsiderTrades Class Constructor.
        """
        self.trades_dir: Path = DATA_DIR_PATH.joinpath('trades')

        # Filings Screener
        self.screener_name = 'latest_insider_trades'
        self.screener = SECFilingsScreener(self.screener_name,
                                           form="4",
                                           count=100)

        # Cached Data
        self.latest_filings: pd.DataFrame | None = None

    def get_latest_filings(self) -> pd.DataFrame:
        """
        Get the latest insider trades filings.
        """

        # Get the latest filings
        latest_filings = self.screener.get_filings()

        # Cache the latest filings
        self.latest_filings = latest_filings

        # Return the latest trades
        return latest_filings

    def parse_filings(self, filings: pd.DataFrame | None = None) -> pd.DataFrame:
        """
        Parse filings to get trade data.

        :param filings: Filings DataFrame. If None, uses the latest filings.
        :return: Trades DataFrame. cols = ['issuer', 'owner', 'non_derivative', 'derivative']
        """

        # Get the latest filings if filings is None
        if filings is None:
            filings = self.latest_filings if self.latest_filings is not None else self.get_latest_filings()

        # Initialize parsed filings DataFrame
        df = pd.DataFrame(columns=['issuer', 'owner', 'non_derivative', 'derivative'])

        # Iterate through each row
        for index, row in filings.iterrows():
            parsed_row = parse_trade(row)

            # Rarely, the trade data is not available for a given filing.
            if parsed_row is not None:
                # Create a new row from parsed row data
                df.loc[index] = [parsed_row['issuer'],
                                 parsed_row['owner'],
                                 parsed_row['non_derivative'],
                                 parsed_row['derivative']]

        return df


def parse_trade(trade: pd.Series) -> dict[str, pd.DataFrame | None] | None:
    """
    Parse a trade.

    :param trade: Trade data row from the SEC filings.
    :return: Parsed trade. None if trade data is not available.
    """

    # Get trade info
    acc_no = trade.name
    filing_link = trade['link']

    # Parse Filing
    filing_parser = SECFilingParser(f'{acc_no}', filing_link)
    doc_url = filing_parser.get_document_url(prefer_xml=True)

    if doc_url is None:
        return None

    # Parse Form
    form_parser = Form4Parser(f'{acc_no}', doc_url)
    trade_data = form_parser.parse()

    return trade_data
