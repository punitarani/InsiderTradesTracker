# Dash App Tables Templates

from dash import dash_table


def build_latest_filings_table() -> dash_table.DataTable:
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

    style_table = {'height': '350px',
                   'overflowY': 'auto'}

    css_data = [{"selector": ".show-hide",
                 "rule": "display: none"}]

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
