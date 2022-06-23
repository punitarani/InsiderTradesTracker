"""
Dash App Base Templates
"""

from dash import html


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
                ],
                style={
                    'textAlign': 'center',
                    'padding': 25
                },
            ),
        ],
        style={
            'padding': 0,
            'margin': 0,
        },
    )

    return _banner
