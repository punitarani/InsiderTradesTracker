"""
Dash App Home Page
"""

from copy import deepcopy
from datetime import datetime

import dash
import numpy as np
import pandas as pd
import pytz
from dash import html, Input, Output, callback
from dash.exceptions import PreventUpdate

from tracker.manage import LatestInsiderTrades
from tracker.parser import SECFilingParser, Form4Parser

from pages.templates.tables import build_latest_filings_table
from pages.templates.sections import build_select_filing_section

# Register Page to App
dash.register_page(__name__, path='/')

# region Global Variables and Caches

# Define Latest Insider Trades Manager
manager: LatestInsiderTrades = LatestInsiderTrades()

# Cache filings DataFrame
filings: pd.DataFrame

# Update Times
update_times: dict = {
    'table-latest-filings': datetime.today(),
}

# Last selected filing url
last_selected_filing_url: str | None = None


# endregion Global Variables and Caches


# region App Callbacks

@callback(
    Output(component_id='table-latest-filings', component_property='data'),
    Output(component_id='latest-filings-updated', component_property='children'),
    Input(component_id='latest-filings-title', component_property='n_clicks')
)
def update_filings_table(n_clicks):
    """
    Update the Latest Filings Table with the latest filings.
    This function is called when the latest filings title is clicked
    It is also called when the app is loaded initially.
    Update every 10 seconds.
    """

    if n_clicks is None or (datetime.now() - update_times['table-latest-filings']).seconds > 10:
        # Get the latest filings
        df = get_filings()

        # pylint: disable=invalid-name,global-statement
        # Cache the latest filings DataFrame
        global filings
        filings = df

        # Reset Index and rename index columns as 'id'
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'id'}, inplace=True)
        # 'id' is used in 'active cell' callbacks to get 'row_id'
        # Allows working with multiple page tables

        # Update the update time
        update_times.update({'table-latest-filings': datetime.now()})

        # Convert to dict
        data = df.to_dict('records')

        # Get datetime EST
        dt_est = datetime.now(pytz.timezone('US/Eastern')).strftime('%H:%M:%S')

        return data, f"Updated: {dt_est} EST"

    # Do Not Update if no changes need to be made
    raise PreventUpdate


# pylint: disable=too-many-locals
@callback(
    Output('select-filing-title', 'children'),
    Output('select-filing-title', 'href'),
    Output('select-filing-section', 'style'),
    Output('table-select-filing-issuer', 'data'),
    Output('table-select-filing-owner-1', 'data'),
    Output('table-select-filing-owner-2', 'data'),
    Output('table-select-filing-non-derivative', 'data'),
    Output('table-select-filing-derivative', 'data'),
    Input('table-latest-filings', 'active_cell')
)
def update_select_filing_section(active_cell):
    """
    Update Select Filing Section when a Filing is selected
    """

    global filings, last_selected_filing_url

    if active_cell is None and last_selected_filing_url is None:
        output_data = [
            # title: children
            "Select a Filing to view details.",

            # title: href
            "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent",

            # section: style
            {'display': 'none'},

            # issuer: data
            [],

            # owner-1: data
            [
                {"index": "Name"},
                {"index": "Street1"},
                {"index": "Street2"},
                {"index": "City"},
                {"index": "State"},
                {"index": "Zip Code"},
                {"index": "State Description"},
            ],

            # owner-2: data
            [
                {"index": "CIK"},
                {"index": "Director"},
                {"index": "Officer"},
                {"index": "10% Owner"},
                {"index": "Other"},
                {"index": "Officer Title"},
                {"index": "Other Text"},
            ],

            # non-derivative: data
            [],

            # derivative: data
            [],
        ]
        return output_data

    if active_cell is not None:
        # Check if filings exists
        try:
            # Get the selected row data from the filings DataFrame
            select_filing = filings.iloc[active_cell['row_id']]
        except NameError:
            # Get and Cache the latest filings DataFrame
            filings = get_filings()

            # Get the selected row data from the filings DataFrame
            select_filing = filings.iloc[active_cell['row_id']]

        # Get Filing Accession Number
        acc_no = select_filing.loc['Filing']
        filing_title = select_filing.loc['Title']
        filing_url = select_filing.loc['Link']

        # Cache selected filing url
        last_selected_filing_url = filing_url

        # Get Filing data
        dfs: dict = get_filing_info(acc_no, filing_url)

        # Get dataframes
        issuer_df = dfs['issuer']
        owner_df = dfs['owner']
        non_der_df = dfs['non_derivative']
        der_df = dfs['derivative']

        # Build selected filing data
        selected_filing_title = f"{acc_no} :\t {filing_title}"

        # Build issuer data
        issuer_data = issuer_df.T.to_dict('records')

        # Build owner data
        # Reset Column names
        owner_df.index.name = "index"
        owner_df.rename(columns={0: "value"}, inplace=True)

        # Filter owner_2 rows
        owner_1_fields = ['Name', 'Street1', 'Street2', 'City',
                          'State', 'Zip Code', 'State Description']
        owner_2_fields = ['CIK', 'Director', 'Officer', '10% Owner',
                          'Other', 'Officer Title', 'Other Text']

        owner_fields = owner_1_fields + owner_2_fields
        # Create fields in owner_df if they don't exist
        for field in owner_fields:
            if field not in owner_df.index:
                owner_df.loc[field] = np.NAN

        # Filter owner_1 rows
        owner_1_df = owner_df.loc[['Name',
                                   'Street1',
                                   'Street2',
                                   'City',
                                   'State',
                                   'Zip Code',
                                   'State Description']]
        # Filter owner_2 rows
        owner_2_df = owner_df.loc[['CIK',
                                   'Director',
                                   'Officer',
                                   '10% Owner',
                                   'Other',
                                   'Officer Title',
                                   'Other Text']]

        # Replace true/false or 1/0 with Yes/No
        owner_2_df.replace('true', 'Yes', inplace=True)
        owner_2_df.replace('false', 'No', inplace=True)
        owner_2_df.replace('1', 'Yes', inplace=True)
        owner_2_df.replace('0', 'No', inplace=True)

        # Reset index to also include index when converting to dict
        owner_1_df.reset_index(inplace=True)
        owner_2_df.reset_index(inplace=True)

        # Convert to dict
        owner_1_data = owner_1_df.to_dict('records')
        owner_2_data = owner_2_df.to_dict('records')

        # Build non-derivative data
        if non_der_df is not None:
            non_der_fields = [
                "securityTitle", "transactionDate", "deemedExecutionDate", "transactionFormType",
                "transactionCode", "equitySwapInvolved", "transactionTimeliness",
                "transactionShares", "transactionPricePerShare", "transactionAcquiredDisposedCode",
                "sharesOwnedFollowingTransaction", "directOrIndirectOwnership", "natureOfOwnership",
            ]

            # Create fields (columns) in non_der_df if they don't exist
            for field in non_der_fields:
                if field not in non_der_df.columns:
                    non_der_df[field] = np.NAN

            # Convert df to 'data' dict
            non_der_data = non_der_df.to_dict('records')
        else:
            non_der_data = []

        # Build derivative data
        if der_df is not None:
            der_fields = [
                "securityTitle", "conversionOrExercisePrice", "transactionDate",
                "transactionCoding", "transactionTimeliness", "transactionAmounts", "exerciseDate",
                "expirationDate", "underlyingSecurityTitle", "underlyingSecurityShares",
                "sharesOwnedFollowingTransaction", "directOrIndirectOwnership", "natureOfOwnership",
            ]

            # Create fields (columns) in der_df if they don't exist
            for field in der_fields:
                if field not in der_df.columns:
                    der_df[field] = np.NAN

            # Convert df to 'data' dict
            der_data = der_df.to_dict('records')
        else:
            der_data = []

        # Build Output data
        output_data = [
            # title: children
            selected_filing_title,

            # title: href
            last_selected_filing_url,

            # section: style
            {},

            # issuer: data
            issuer_data,

            # owner-1: data
            owner_1_data,

            # owner-2: data
            owner_2_data,

            # non-derivative: data
            non_der_data,

            # derivative: data
            der_data,
        ]

        return output_data

    # Do Not Update if no changes need to be made
    raise PreventUpdate


# endregion App Callbacks


# region Helper Functions

def get_filings() -> pd.DataFrame:
    """
    Get the Latest Filings Data.
    :return: Formatted Latest Insider Trades Filings
    """

    # Get the latest filings
    _filings = manager.get_latest_filings()
    df = deepcopy(_filings)

    # Reset index
    df.reset_index(inplace=True)

    # Remove form type from title columns
    df['title'] = df.apply(axis=1,
                           func=lambda x: str(x['title']).replace(f'{x.form_type} - ', ''))

    # Format DateTime
    df['date_time'] = df.apply(axis=1, func=lambda x: x['date_time'].strftime('%Y-%m-%d %H:%M:%S'))

    # Drop form_type column
    df = df.drop(['form_type'], axis=1, inplace=False)

    # Convert DateTime column to string

    # Rename Columns
    df = df.rename(
        columns={
            'acc': 'Filing',
            'title': 'Title',
            'date_time': 'DateTime',
            'link': 'Link'
        },
        inplace=False)

    # Cache the filings DataFrame
    global filings
    filings = df

    return df


def get_filing_info(filing: str, url: str) -> dict:
    """
    Get the Filing Info
    :param filing: Filing Accession Number
    :param url: Filing URL
    """
    # Get document url from filing
    filing_parser = SECFilingParser(filing, url)
    form_url = filing_parser.get_document_url(prefer_xml=True)

    # Get parsed dataframes from form
    form_parser = Form4Parser(filing, form_url)
    dfs: dict = form_parser.parse()

    # Format Issuer df
    issuer_df = dfs['issuer']
    # Rename Index to match DataTable
    issuer_df.rename(index={
        "issuerName": "Name",
        "issuerTradingSymbol": "Symbol",
        "issuerCik": "CIK",
    }, inplace=True)

    # Format Owner df
    owner_df = dfs['owner']
    # Rename Index to match DataTable
    owner_df.rename(index={
        "Id.Cik": "CIK",
        "Id.Name": "Name",
        "Address.Street1": "Street1",
        "Address.Street2": "Street2",
        "Address.City": "City",
        "Address.State": "State",
        "Address.ZipCode": "Zip Code",
        "Address.StateDescription": "State Description",
        "Relationship.isDirector": "Director",
        "Relationship.isOfficer": "Officer",
        "Relationship.isTenPercentOwner": "10% Owner",
        "Relationship.isOther": "Other",
        "Relationship.officerTitle": "Officer Title",
        "Relationship.otherText": "Other Text"
    }, inplace=True)

    # Format Non-Derivative df
    non_der_df = dfs['non_derivative']

    # Rename Columns to match DataTable column 'id'
    if non_der_df is not None and non_der_df.shape[0] > 0:
        non_der_df.rename(columns={
            "securityTitle": "securityTitle",
            "transactionDate": "transactionDate",
            "deemedExecutionDate": "deemedExecutionDate",
            "transactionCoding.transactionFormType": "transactionFormType",
            "transactionCoding.transactionCode": "transactionCode",
            "transactionCoding.equitySwapInvolved": "equitySwapInvolved",
            "transactionTimeliness": "transactionTimeliness",

            "transactionAmounts.transactionShares": "transactionShares",
            "transactionAmounts.transactionPricePerShare": "transactionPricePerShare",
            "transactionAmounts.transactionAcquiredDisposedCode": "transactionAcquiredDisposedCode",

            "postTransactionAmounts.sharesOwnedFollowingTransaction":
                "sharesOwnedFollowingTransaction",

            "ownershipNature.directOrIndirectOwnership": "directOrIndirectOwnership",
            "ownershipNature.natureOfOwnership": "natureOfOwnership",
        }, inplace=True)
    # Set to None if empty
    else:
        non_der_df = None

    # Format Derivative df
    der_df = dfs['derivative']

    # Rename Columns to match DataTable column 'id'
    if der_df is not None and der_df.shape[0] > 0:
        der_df.rename(columns={
            "securityTitle": "securityTitle",
            "conversionOrExercisePrice": "conversionOrExercisePrice",
            "transactionDate": "transactionDate",
            "transactionCoding": "transactionCoding",
            "transactionTimeliness": "transactionTimeliness",
            "transactionAmounts": "transactionAmounts",
            "exerciseDate.footnoteId": "exerciseDate",
            "expirationDate": "expirationDate",

            "underlyingSecurity.underlyingSecurityTitle": "underlyingSecurityTitle",
            "underlyingSecurity.underlyingSecurityShares": "underlyingSecurityShares",

            "postTransactionAmounts.sharesOwnedFollowingTransaction":
                "sharesOwnedFollowingTransaction",

            "ownershipNature.directOrIndirectOwnership": "directOrIndirectOwnership",
            "ownershipNature.natureOfOwnership": "natureOfOwnership",
        }, inplace=True)
    # Set to None if empty
    else:
        der_df = None

    # Update dfs dict
    dfs.update({
        'issuer': issuer_df,
        'owner': owner_df,
        'non_derivative': non_der_df,
        'derivative': der_df,
    })

    return dfs


# endregion Helper Functions


# Define Home Page Layout
layout = html.Div(
    id="big-app-container",
    children=[
        # Header
        html.H2(
            children="Realtime SEC Form 4 Tracker",
            style={
                'textAlign': 'center',
            },
        ),

        # Latest Filings Table
        html.Div(
            id='latest-filings-container',
            children=[
                html.Div(
                    id='latest-filings-text-container',
                    children=[
                        html.H2('Latest Filings',
                                id='latest-filings-title',
                                style={
                                    'textAlign': 'left',
                                    'padding-left': 5,
                                    'margin-bottom': 5,
                                }),

                        html.Em(children=None,
                                id='latest-filings-updated',
                                style={
                                    'fontSize': 14,
                                    'textAlign': 'left',
                                    'padding': 5,
                                    'margin-top': 5,
                                    'margin-bottom': 20,
                                }),
                    ],
                    style={
                        'padding': 5,
                        'margin-top': -25,
                    }
                ),

                build_latest_filings_table(),
            ],
            style={'padding': 5},
        ),

        # Selected Filing Section
        html.Div(
            id='select-filing-container',
            children=[
                html.H2(
                    'Selected Filing',
                    id='selected-filing-title',
                    style={
                        'padding': 0,
                        'margin-bottom': 0,
                    }
                ),

                # Filing Title
                html.A(
                    children='Select a Filing to View Details',
                    id='select-filing-title',
                    href="",
                    target='_blank',
                    style={
                        'padding': 0,
                        'margin-top': 5,
                        'margin-bottom': 5
                    },
                ),

                # Filing Tables
                build_select_filing_section(),
            ],
            style={
                'padding': 5,
                'margin-top': 0,
            },
        ),
    ],
    style={
        'padding': 0,
        'margin-top': -50,
    },
)
