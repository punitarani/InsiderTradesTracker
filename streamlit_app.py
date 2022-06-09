# Streamlit App

from copy import deepcopy

import pandas as pd
import streamlit as st

from tracker.manage import LatestInsiderTrades

# Define Latest Insider Trades Manager
manager = LatestInsiderTrades()


def main_page():
    """
    Streamlit App Main Page
    """

    # Config
    st.set_page_config(page_title='Latest Trades', page_icon='📈', layout='wide')
    st.title("Insider Trades Tracker")

    # Get the latest insider trades filings
    df = get_latest_trades()

    # Display the dataframe
    st.write(df, unsafe_allow_html=True)


# region Helper Functions
def get_latest_trades() -> pd.DataFrame:
    """
    Get the latest insider trades filings
    :return: Formatted Filings DataFrame
    """

    # Get the latest insider trades filings
    filings = manager.get_latest_filings()
    df: pd.DataFrame = deepcopy(filings)

    def make_clickable(link, text):
        return f'<a href="{link}" target="_blank">{text}</a>'

    # Combine the title and link to create a clickable link
    df['Filing'] = df[['title', 'link']].apply(lambda row: make_clickable(row['link'], row['title']), axis=1)

    # Get selected columns
    df = df[['form_type', 'date_time', 'Filing']]

    # Format the dataframe
    df.reset_index(inplace=True)
    df.rename(columns={'form_type': 'Form', 'date_time': 'Date', 'Filing': 'Filing'}, inplace=True)
    df = df.to_html(escape=False)

    return df
# endregion


# Call Page
main_page()
