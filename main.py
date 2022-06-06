# Main file

import pandas as pd

from tracker.manage import LatestInsiderTrades

if __name__ == '__main__':
    # Initialize the LatestInsiderTrades class
    manager = LatestInsiderTrades()
    print("Insider Trades Tracker.")

    # Get the latest filings
    print("Getting the latest filings...")
    latest_filings = manager.get_latest_filings()
    print(f"Found {len(latest_filings)} filings.")

    # Print the Latest Filings
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.colheader_justify', 'center')
    pd.set_option('display.precision', 3)
    print(latest_filings)

    # Parse the filings
    # print("Parsing the filings...")
    # trades = manager.parse_filings(latest_filings)
