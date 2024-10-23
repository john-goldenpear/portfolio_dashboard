from dash import dcc, html, Input, Output, callback
import pandas as pd

# Load your Excel data into a DataFrame
df = pd.read_excel('output/positions.xlsx')

# Define the layout
layout = html.Div(
    style={'backgroundColor': '#000000', 'color': '#FFFFFF', 'padding': '20px', 'fontFamily': 'Rajdhani'},
    children=[
        html.H1(
            "Portfolio Detail",
            style={
                'textAlign': 'left',
                'fontSize': '48px',
                'fontWeight': 'normal',
                'margin': '0',
                'borderBottom': '3px solid rgb(52,224,190)',
                'paddingBottom': '5px'
            }
        ),
        # Row for Dropdown and Boxes
        html.Div(
            className='flex-container',  # Use the CSS class for flex container
            children=[
                # Dropdown for Strategy Selection
                dcc.Dropdown(
                    id='strategy-dropdown',
                    options=[
                        {'label': 'All', 'value': 'All'},
                        {'label': 'Quality', 'value': 'Quality'},
                        {'label': 'Delta Neutral', 'value': 'Delta Neutral'},
                        {'label': 'Discretionary', 'value': 'Discretionary'}
                    ],
                    value='All',  # Default value
                    className='dropdown'  # Use the CSS class for dropdown
                ),
                # Metrics Boxes
                html.Div(
                    id='asset-metrics-boxes',
                    style={'display': 'flex', 'justifyContent': 'flex-start'},
                    children=[]
                )
            ]
        ),
        # Add content for the Portfolio Detail page here
    ]
)

# Callback to update the metrics based on the selected strategy
@callback(
    Output('asset-metrics-boxes', 'children'),  # Use the new unique ID
    [Input('strategy-dropdown', 'value')]
)
def update_metrics(selected_strategy):
    # Filter the DataFrame based on the selected strategy
    if selected_strategy != 'All':
        filtered_df = df[df['strategy'] == selected_strategy]
    else:
        filtered_df = df

    # Recalculate metrics
    total_equity_value = filtered_df['equity'].sum()
    total_notional_value = filtered_df['notional'].sum()
    portfolio_leverage = total_notional_value / total_equity_value if total_equity_value != 0 else 0
    market_exposure = filtered_df[filtered_df['asset_type'] != 'STABLE']['value'].sum() / total_equity_value if total_equity_value != 0 else 0
    market_beta = (filtered_df['beta_daily'] * filtered_df['value']).sum() / total_equity_value if total_equity_value != 0 else 0
    free_equity_value = filtered_df[~filtered_df['position_type'].isin(['vesting', 'locked'])]['equity'].sum()
    free_notional_value = filtered_df[~filtered_df['position_type'].isin(['vesting', 'locked'])]['notional'].sum()
    free_leverage_value = free_notional_value / free_equity_value if free_equity_value != 0 else 0

    # Return the updated boxes with small spaces between them
    return [
        html.Div(
            style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'width': '150px', 'textAlign': 'center'},
            children=[
                html.H1(f"{total_equity_value / 1_000_000:.1f}M", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                html.H3("Equity", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
            ]
        ),
        html.Div(style={'width': '20px'}),  # Small space between boxes
        html.Div(
            style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'width': '150px', 'textAlign': 'center'},
            children=[
                html.H1(f"{total_notional_value / 1_000_000:.1f}M", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                html.H3("Notional", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
            ]
        ),
        html.Div(style={'width': '20px'}),  # Small space between boxes
        html.Div(
            style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'width': '150px', 'textAlign': 'center'},
            children=[
                html.H1(f"{portfolio_leverage:.2f}", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                html.H3("Leverage", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
            ]
        ),
        html.Div(style={'width': '20px'}),  # Small space between boxes
        html.Div(
            style={'border': '1px solid #FFFFFF', 'padding': '13px', 'width': '150px', 'textAlign': 'center'},
            children=[
                html.H1(f"{market_exposure:.2f}", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                html.H3("Market Exposure", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
            ]
        ),
        html.Div(style={'width': '20px'}),  # Small space between boxes
        html.Div(
            style={'border': '1px solid #FFFFFF', 'padding': '13px', 'width': '150px', 'textAlign': 'center'},
            children=[
                html.H1(f"{market_beta:.2f}", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                html.H3("Market (BTC) Beta", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
            ]
        ),
        html.Div(style={'width': '20px'}),  # Small space between boxes
        html.Div(
            style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'width': '150px', 'textAlign': 'center'},
            children=[
                html.H1(f"{free_equity_value / 1_000_000:.1f}M", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                html.H3("Free Equity", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
            ]
        ),
        html.Div(style={'width': '20px'}),  # Small space between boxes
        html.Div(
            style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'width': '150px', 'textAlign': 'center'},
            children=[
                html.H1(f"{free_leverage_value:.2f}", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                html.H3("Free Leverage", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
            ]
        )
    ]
