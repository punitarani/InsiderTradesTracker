# Dash App Section Templates

from dash import html, dash_table


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

            {"name": ["Ownership", "Nature"],
             "id": "natureOfOwnership"},
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

            {'if': {'column_id': 'transactionShares'},
             'width': '12.5%', 'textAlign': 'right', },

            {'if': {'column_id': 'transactionPricePerShare'},
             'width': '10%', 'textAlign': 'right', },

            {'if': {'column_id': 'sharesOwnedFollowingTransaction'},
             'width': '12.5%', 'textAlign': 'right', },

            {'if': {'column_id': 'directOrIndirectOwnership'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'natureOfOwnership'},
             'width': '5%', 'textAlign': 'center', }
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

            {"name": ["Ownership", "Nature"],
             "id": "natureOfOwnership"}
        ],
        merge_duplicate_headers=True,
        fixed_rows={'headers': True},
        style_header={'textAlign': 'center'},
        style_cell_conditional=[
            {'if': {'column_id': 'securityTitle'},
             'width': '17.5%', 'textAlign': 'left', },

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
             'width': '12.5%', 'textAlign': 'right', },

            {'if': {'column_id': 'directOrIndirectOwnership'},
             'width': '5%', 'textAlign': 'center', },

            {'if': {'column_id': 'natureOfOwnership'},
             'width': '5%', 'textAlign': 'center', }
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
