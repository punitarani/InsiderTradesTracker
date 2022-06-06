# Streamlit App

import streamlit as st

from tracker.manage import LatestInsiderTrades


def main_page():
    """
    Streamlit App Main Page
    """
    st.title("Insider Trades Tracker")

    # Initialize the LatestInsiderTrades class
    manager = LatestInsiderTrades()

    # Get the latest filings
    filings = manager.get_latest_filings()

    # Display the latest filings
    st.table(filings)


# Call Page
main_page()
