# Dash App Base Templates

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
