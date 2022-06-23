"""
Dash App
"""

import dash
from dash import Dash, html

import config
from pages.templates.base import build_banner


# Create Dash App
app = Dash(name='Insider Trades Tracker',
           use_pages=True)

# Define Server
server = app.server

# Define App Title
app.title = 'Tracker'


# Define App Layout
app.layout = html.Div(
    id="big-app-container",
    children=[
        # Website Metadata
        html.Title('Tracker',
                   id='title'),

        # Header data
        build_banner(),

        # Pages Content
        dash.page_container,
    ],
    style={'padding': 10},
)


# Run App
if __name__ == '__main__':
    # Development
    if config.DEPLOYMENT == 'D':
        app.run_server(debug=True)

    # Production
    else:
        app.run_server(debug=False)
