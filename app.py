# Dashboard Application

from copy import deepcopy
from datetime import datetime

import dash
import numpy as np
import pandas as pd
import pytz
from dash import Dash, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate

from tracker.manage import LatestInsiderTrades
from tracker.parser import SECFilingParser, Form4Parser

# region Global Variables and Caches

# Define Latest Insider Trades Manager
manager: LatestInsiderTrades = LatestInsiderTrades()

# Cache filings DataFrame
filings: pd.DataFrame

# Update Times
update_times: dict = {
    'table-latest-filings': -1,
}

# Last selected filing url
last_selected_filing_url: str | None = None

# Define App
app = Dash('Insider Trades Tracker')
app.title = 'Tracker'


# endregion


# region App Callbacks

def _cb_highlight_row_filings(cell):
    if cell is None:
        return dash.no_update
    return [
        {"if": {"filter_query": "{{id}} ={}".format(i)}, "backgroundColor": "white"}
        for i in [cell['row_id']]
    ]


@callback(
    Output(component_id='table-latest-filings', component_property='data'),
    Output(component_id='latest-filings-updated', component_property='children'),
    Input(component_id='latest-filings-title', component_property='n_clicks')
)
def update_filings_table(n_clicks):
    """
    Update the Latest Filings Table with the latest filings.
    This function is called when the latest filings title is clicked but also initially when the app is loaded.
    Update every 10 seconds.
    """

    if n_clicks is None or (datetime.now() - update_times['table-latest-filings']).seconds > 10:
        # Get the latest filings
        df = get_filings()

        # Reset Index and rename index columns as 'id'
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'id'}, inplace=True)
        # 'id' is used in 'active cell' callbacks to get 'row_id' to accommodate for multiple page tables

        # Update the update time
        update_times.update({'table-latest-filings': datetime.now()})

        # Convert to dict
        data = df.to_dict('records')

        return data, 'Updated: {} EST'.format(datetime.now(pytz.timezone('US/Eastern')).strftime('%H:%M:%S'))

    else:
        raise PreventUpdate


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

    elif active_cell is not None:
        # Get Filing Accession Number
        acc_no = filings.iloc[active_cell['row_id']].loc['Filing']
        filing_title = filings.iloc[active_cell['row_id']].loc['Title']
        filing_url = filings.iloc[active_cell['row_id']].loc['Link']

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
        owner_1_fields = ['Name', 'Street1', 'Street2', 'City', 'State', 'Zip Code', 'State Description']
        owner_2_fields = ['CIK', 'Director', 'Officer', '10% Owner', 'Other', 'Officer Title', 'Other Text']

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
                "securityTitle", "transactionDate", "deemedExecutionDate", "transactionFormType", "transactionCode",
                "equitySwapInvolved", "transactionTimeliness", "transactionShares", "transactionPricePerShare",
                "transactionAcquiredDisposedCode", "sharesOwnedFollowingTransaction", "directOrIndirectOwnership",
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
                "securityTitle", "conversionOrExercisePrice", "transactionDate", "transactionCoding",
                "transactionTimeliness", "transactionAmounts", "exerciseDate", "expirationDate",
                "underlyingSecurityTitle",
                "underlyingSecurityShares", "sharesOwnedFollowingTransaction", "directOrIndirectOwnership"
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

    else:
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
    df['title'] = df.apply(axis=1, func=lambda x: x['title'].__str__().replace(f'{x.form_type} - ', ''))

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
            "postTransactionAmounts.sharesOwnedFollowingTransaction": "sharesOwnedFollowingTransaction",
            "ownershipNature.directOrIndirectOwnership": "directOrIndirectOwnership",
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
            "postTransactionAmounts.sharesOwnedFollowingTransaction": "sharesOwnedFollowingTransaction",
            "ownershipNature.directOrIndirectOwnership": "directOrIndirectOwnership",
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


# region App Components

def build_banner() -> html.Div:
    """
    Build the Website Header Banner
    """
    _banner = html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H1("Insider Trades Tracker"),
                    html.H2("Realtime SEC Form 4 Tracker",
                            style={'margin-top': -15}),
                ],
                style={
                    'textAlign': 'center',
                    'padding': 25
                },
            ),
        ],
    )

    return _banner


def build_filings_table() -> dash_table.DataTable:
    """
    Create Blank Filings Table

    Table ID:
        table-latest-filings
    """

    data = []

    columns = [
        {'name': 'Filing', 'id': 'Filing'},
        {'name': 'Title', 'id': 'Title'},
        {'name': 'DateTime', 'id': 'DateTime'},
        {'name': 'id', 'id': 'id'},
    ]

    # Define style dicts
    style_header = {
        'textAlign': 'left',
    }

    style_data = {
        'textAlign': 'left'
    }

    style_cell_conditional = [
        {'if': {'column_id': 'Filing'},
         'width': '35%'},
        {'if': {'column_id': 'Title'},
         'width': '55%'},
    ]

    style_table = {'height': '350px', 'overflowY': 'auto'}

    css_data = [{"selector": ".show-hide", "rule": "display: none"}]

    # Construct Data Table.
    data_table = dash_table.DataTable(
        data=data,
        columns=columns,
        hidden_columns=['id'],
        id='table-latest-filings',
        style_as_list_view=True,
        fixed_rows={'headers': True},
        page_size=25,
        style_header=style_header,
        style_data=style_data,
        style_table=style_table,
        style_cell_conditional=style_cell_conditional,
        css=css_data
    )

    return data_table


def build_select_filing_section() -> html.Div:
    """
    Build the Select Filing Section

    Table IDs:
        table-select-filing-issuer

        table-select-filing-owner-1

        table-select-filing-owner-2

        table-select-filing-non-derivative

        table-select-filing-derivative
    """

    # Fields
    """
    Issuer
    ['issuerCik', 'issuerName', 'issuerTradingSymbol']
    
    Owner
    ['Id.Cik', 'Id.Name', 'Address.Street1', 'Address.Street2',
       'Address.City', 'Address.State', 'Address.ZipCode',
       'Address.StateDescription', 'Relationship.isDirector',
       'Relationship.isOfficer', 'Relationship.isTenPercentOwner',
       'Relationship.isOther', 'Relationship.officerTitle',
       'Relationship.otherText']
       
    Non-Derivative
    [{'id': 'securityTitle', 'name': 'securityTitle'},
    {'id': 'transactionDate', 'name': 'transactionDate'},
    {'id': 'deemedExecutionDate', 'name': 'deemedExecutionDate'},
    {'id': 'transactionCoding.transactionFormType', 'name': 'transactionCoding.transactionFormType'},
    {'id': 'transactionCoding.transactionCode', 'name': 'transactionCoding.transactionCode'},
    {'id': 'transactionCoding.equitySwapInvolved', 'name': 'transactionCoding.equitySwapInvolved'},
    {'id': 'transactionTimeliness', 'name': 'transactionTimeliness'},
    {'id': 'transactionAmounts.transactionShares', 'name': 'transactionAmounts.transactionShares'},
    {'id': 'transactionAmounts.transactionPricePerShare', 'name': 'transactionAmounts.transactionPricePerShare'},
    {'id': 'transactionAmounts.transactionAcquiredDisposedCode', 
        'name': 'transactionAmounts.transactionAcquiredDisposedCode'},
    {'id': 'postTransactionAmounts.sharesOwnedFollowingTransaction',
        'name': 'postTransactionAmounts.sharesOwnedFollowingTransaction'},
    {'id': 'ownershipNature.directOrIndirectOwnership', 'name': 'ownershipNature.directOrIndirectOwnership'}]

    Derivative
    [{'id': 'securityTitle', 'name': 'securityTitle'},
    {'id': 'conversionOrExercisePrice', 'name': 'conversionOrExercisePrice'},
    {'id': 'transactionDate', 'name': 'transactionDate'},
    {'id': 'transactionCoding', 'name': 'transactionCoding'},
    {'id': 'transactionTimeliness', 'name': 'transactionTimeliness'},
    {'id': 'transactionAmounts', 'name': 'transactionAmounts'},
    {'id': 'exerciseDate.footnoteId', 'name': 'exerciseDate.footnoteId'},
    {'id': 'expirationDate', 'name': 'expirationDate'},
    {'id': 'underlyingSecurity.underlyingSecurityTitle', 'name': 'underlyingSecurity.underlyingSecurityTitle'},
    {'id': 'underlyingSecurity.underlyingSecurityShares', 'name': 'underlyingSecurity.underlyingSecurityShares'},
    {'id': 'postTransactionAmounts.sharesOwnedFollowingTransaction',
        'name': 'postTransactionAmounts.sharesOwnedFollowingTransaction'},
    {'id': 'ownershipNature.directOrIndirectOwnership', 'name': 'ownershipNature.directOrIndirectOwnership'}]
    """

    # region issuer table
    issuer_table = dash_table.DataTable(
        id='table-select-filing-issuer',
        columns=[{"name": i, "id": i} for i in ["Name", "Symbol", "CIK"]],
        data=[],
        style_as_list_view=True,
        style_header={'textAlign': 'center'},
        style_data={'textAlign': 'center'},
        style_cell_conditional=[
            {'if': {'column_id': 'Name'},
             'width': '40%'},
            {'if': {'column_id': 'Symbol'},
             'width': '20%'},
            {'if': {'column_id': 'CIK'},
             'width': '40%'},
        ],
    )
    # endregion issuer table

    # region owner table
    _owner_table_1 = dash_table.DataTable(
        id='table-select-filing-owner-1',
        columns=[{"name": i, "id": i} for i in ["index", "value"]],
        data=[
            {"index": "Name"},
            {"index": "Street1"},
            {"index": "Street2"},
            {"index": "City"},
            {"index": "State"},
            {"index": "Zip Code"},
            {"index": "State Description"},
        ],
        style_header={'display': 'none'},
        css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
        style_cell_conditional=[
            {'if': {'column_id': 'index'},
             'width': '50%'},
            {'if': {'column_id': 'value'},
             'width': '50%'},
        ],
    )

    _owner_table_2 = dash_table.DataTable(
        id='table-select-filing-owner-2',
        columns=[{"name": i, "id": i} for i in ["index", "value"]],
        data=[
            {"index": "CIK"},
            {"index": "Director"},
            {"index": "Officer"},
            {"index": "10% Owner"},
            {"index": "Other"},
            {"index": "Officer Title"},
            {"index": "Other Text"},
        ],
        style_header={'display': 'none'},
        css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
        style_cell_conditional=[
            {'if': {'column_id': 'index'},
             'width': '50%'},
            {'if': {'column_id': 'value'},
             'width': '50%'},
        ],
    )
    # endregion owner table

    # region non derivative table
    non_derivative_table = dash_table.DataTable(
        id='table-select-filing-non-derivative',
        data=[],
        columns=[
            {"name": ["", "Security"],
             "id": "securityTitle"},

            {"name": ["Date", "Transaction"],
             "id": "transactionDate"},

            {"name": ["Date", "Execution"],
             "id": "deemedExecutionDate"},

            {"name": ["Transaction Coding", " Form"],
             "id": "transactionFormType"},

            {"name": ["Transaction Coding", "Code"],
             "id": "transactionCode"},

            {"name": ["Transaction Coding", "Eqt Swap"],
             "id": "equitySwapInvolved"},

            {"name": ["Transaction Coding", "Timeliness"],
             "id": "transactionTimeliness"},

            {"name": ["Transaction Amounts", "Shares"],
             "id": "transactionShares"},

            {"name": ["Transaction Amounts", "Price/Share"],
             "id": "transactionPricePerShare"},

            {"name": ["Transaction Amounts", "Code"],
             "id": "transactionAcquiredDisposedCode"},

            {"name": ["Post Transaction", "Shares Owned"],
             "id": "sharesOwnedFollowingTransaction"},

            {"name": ["Ownership", "Code"],
             "id": "directOrIndirectOwnership"},
        ],
        merge_duplicate_headers=True,
        fixed_rows={'headers': True},
        style_header={'textAlign': 'center'},
        style_cell_conditional=[
            {'if': {'column_id': 'securityTitle'},
             'width': '20%', 'textAlign': 'left', },

            {'if': {'column_id': 'transactionDate'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'deemedExecutionDate'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'transactionFormType'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'transactionCode'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'equitySwapInvolved'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'transactionTimeliness'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'transactionAcquiredDisposedCode'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'directOrIndirectOwnership'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'transactionShares'},
             'width': '12.5%', 'textAlign': 'right', },

            {'if': {'column_id': 'transactionPricePerShare'},
             'width': '12.5%', 'textAlign': 'right', },

            {'if': {'column_id': 'sharesOwnedFollowingTransaction'},
             'width': '15%', 'textAlign': 'right', },
        ],
    )
    # endregion non derivative table

    # region derivative table
    derivative_table = dash_table.DataTable(
        id='table-select-filing-derivative',
        columns=[
            {"name": ["", "Security"],
             "id": "securityTitle"},

            {"name": ["Date", "Transaction"],
             "id": "transactionDate"},

            {"name": ["Date", "Expiration"],
             "id": "expirationDate"},

            {"name": ["Date", "Exercise"],
             "id": "exerciseDate"},

            {"name": ["Transaction", "Code"],
             "id": "transactionCoding"},

            {"name": ["Transaction", "Timeliness"],
             "id": "transactionTimeliness"},

            {"name": ["Transaction", "Amounts"],
             "id": "transactionAmounts"},

            {"name": ["Underlying Security", "Title"],
             "id": "underlyingSecurityTitle"},

            {"name": ["Underlying Security", "Shares"],
             "id": "underlyingSecurityShares"},

            {"name": ["Post Transaction", "Shares Owned"],
             "id": "sharesOwnedFollowingTransaction"},

            {"name": ["Ownership", "Code"],
             "id": "directOrIndirectOwnership"},
        ],
        merge_duplicate_headers=True,
        fixed_rows={'headers': True},
        style_header={'textAlign': 'center'},
        style_cell_conditional=[
            {'if': {'column_id': 'securityTitle'},
             'width': '20%', 'textAlign': 'left', },

            {'if': {'column_id': 'transactionDate'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'expirationDate'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'exerciseDate'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'transactionCoding'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'transactionTimeliness'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'transactionAmounts'},
             'width': '10%', 'textAlign': 'right', },

            {'if': {'column_id': 'underlyingSecurityTitle'},
             'width': '15%', 'textAlign': 'center', },

            {'if': {'column_id': 'underlyingSecurityShares'},
             'width': '10%', 'textAlign': 'right', },

            {'if': {'column_id': 'sharesOwnedFollowingTransaction'},
             'width': '15%', 'textAlign': 'right', },

            {'if': {'column_id': 'directOrIndirectOwnership'},
             'width': '5%', 'textAlign': 'center', },
        ],
    )
    # endregion derivative table

    # region filing layout
    filing_layout = html.Div(
        id='select-filing-section',
        children=[
            html.Div(
                id='select-filing-tables-container',
                children=[
                    # Issuer Table
                    html.Div(
                        children=[
                            html.H4('Issuer', style={'padding': 0, 'margin': 0}),
                            issuer_table
                        ],
                        style={'padding': 10, 'flex': 1}),

                    # Owner Tables
                    html.Div(
                        id="table-select-filing-owner-container",
                        children=[
                            html.H4('Owner', style={'padding': 10, 'margin-bottom': -20}),
                            html.Div(
                                children=[
                                    html.Div(_owner_table_1,
                                             style={'padding': 10, 'flex': 1}),
                                    html.Div(_owner_table_2,
                                             style={'padding': 10, 'flex': 1}),
                                ],
                                style={'display': 'flex', 'flex-direction': 'row',
                                       'padding': 0, 'margin-top': -50},
                            ),
                        ],
                        style={'padding': 10, 'flex': 2, 'margin-top': -30},
                    ),

                    # Non Derivative Table
                    html.Div(
                        children=[
                            html.H4('Non-Derivative Transactions', style={'padding': 0, 'margin': 0}),
                            non_derivative_table,
                        ],
                        style={'padding': 10, 'margin-top': 0, 'flex': 3},
                    ),

                    # Derivative Table
                    html.Div(
                        children=[
                            html.H4('Derivative Transactions', style={'padding': 0, 'margin': 0}),
                            derivative_table,
                        ],
                        style={'padding': 10, 'margin-top': 0, 'flex': 4}
                    ),
                ],
                style={'display': 'flex', 'flex-direction': 'column'},
            ),
        ],
        style={'display': 'none'}
    )
    # endregion filing layout

    return filing_layout


# endregion App Components


# region Dash App Layout and Config

def get_layout():
    """
    Get the App Layout
    """

    layout = html.Div(
        id="big-app-container",
        children=[
            # Website Metadata
            html.Title('Tracker',
                       id='title'),

            # Header data
            build_banner(),

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

                    build_filings_table(),
                ],
                style={'padding': 5},
            ),

            # Add Blank Space
            html.Br(),

            # Selected Filing Section
            html.Div(
                id='select-filing-container',
                children=[
                    html.H2(
                        'Selected Filing',
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
                    'margin-top': -40,
                },
            ),
        ],
        style={'padding': 10},
    )

    return layout


app.layout = get_layout()

# endregion Dash App

# Run App
if __name__ == '__main__':
    app.run_server(debug=True,
                   dev_tools_hot_reload=True)
