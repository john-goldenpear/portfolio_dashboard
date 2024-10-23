from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Load your Excel data into a DataFrame
df = pd.read_excel('output/positions.xlsx')

# Calculate market exposure
total_market_value_non_stable = df[df['asset_type'] != 'STABLE']['value'].sum()
total_equity_value = df['equity'].sum()
market_exposure = total_market_value_non_stable / total_equity_value if total_equity_value != 0 else 0

# Calculate allocations
strategy_allocations = df.groupby('strategy')['equity'].sum() / total_equity_value * 100

# Calculate additional metrics
total_notional_value = df['notional'].sum()
portfolio_leverage = total_notional_value / total_equity_value if total_equity_value != 0 else 0

# Calculate Market (BTC) Beta
market_beta = (df['beta_daily'] * df['value']).sum() / total_equity_value if total_equity_value != 0 else 0

# Calculate free equity and free leverage
free_equity_value = df[~df['position_type'].isin(['vesting', 'locked'])]['equity'].sum()
free_notional_value = df[~df['position_type'].isin(['vesting', 'locked'])]['notional'].sum()
free_leverage_value = free_notional_value / free_equity_value if free_equity_value != 0 else 0

layout = html.Div(
    style={'backgroundColor': '#000000', 'color': '#FFFFFF', 'padding': '20px', 'fontFamily': 'Rajdhani'},
    children=[
        html.Link(
            href='https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap',
            rel='stylesheet'
        ),
        html.H1(
            "Portfolio Summary",
            style={
                'textAlign': 'left',
                'fontSize': '48px',
                'fontWeight': 'normal',
                'margin': '0',
                'borderBottom': '3px solid rgb(52,224,190)',
                'paddingBottom': '5px'
            }
        ),
        # Row for Boxes
        html.Div(
            style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 'marginBottom': '40px', 'marginTop': '20px'},
            children=[
                html.Div(
                    style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'flex': '1', 'textAlign': 'center', 'margin': '5px'},
                    children=[
                        html.H1(f"{total_equity_value / 1_000_000:.1f}M", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                        html.H3("Equity", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
                    ]
                ),
                html.Div(
                    style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'flex': '1', 'textAlign': 'center', 'margin': '5px'},
                    children=[
                        html.H1(f"{total_notional_value / 1_000_000:.1f}M", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                        html.H3("Notional", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
                    ]
                ),
                html.Div(
                    style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'flex': '1', 'textAlign': 'center', 'margin': '5px'},
                    children=[
                        html.H1(f"{portfolio_leverage:.2f}", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                        html.H3("Leverage", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
                    ]
                ),
                html.Div(
                    style={'border': '1px solid #FFFFFF', 'padding': '13px', 'flex': '1', 'textAlign': 'center', 'margin': '5px'},
                    children=[
                        html.H1(f"{market_exposure:.2f}", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                        html.H3("Market Exposure", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
                    ]
                ),
                html.Div(
                    style={'border': '1px solid #FFFFFF', 'padding': '13px', 'flex': '1', 'textAlign': 'center', 'margin': '5px'},
                    children=[
                        html.H1(f"{market_beta:.2f}", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                        html.H3("Market (BTC) Beta", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
                    ]
                ),
                html.Div(
                    style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'flex': '1', 'textAlign': 'center', 'margin': '5px'},
                    children=[
                        html.H1(f"{free_equity_value / 1_000_000:.1f}M", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                        html.H3("Free Equity", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
                    ]
                ),
                html.Div(
                    style={'border': '1px solid rgb(52,224,190)', 'padding': '13px', 'flex': '1', 'textAlign': 'center', 'margin': '5px'},
                    children=[
                        html.H1(f"{free_leverage_value:.2f}", style={'fontSize': '34px', 'margin': '0', 'fontWeight': 'normal'}),
                        html.H3("Free Leverage", style={'margin': '0', 'fontSize': '18px', 'fontWeight': 'normal'})
                    ]
                )
            ]
        ),
        # Row for Strategy Metrics and Pie Charts
        html.Div(
            style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 'marginTop': '20px'},
            children=[
                # Strategy Metrics
                html.Div(
                    style={'border': '1px solid #888888', 'padding': '13px', 'flex': '1 1 30%', 'margin': '5px', 'minWidth': '300px'},
                    children=[
                        html.Div(
                            style={'borderLeft': '3px solid rgb(52,224,190)', 'paddingLeft': '10px', 'marginBottom': '20px'},
                            children=[
                                html.H3("Quality", style={'margin': '0', 'fontSize': '24px', 'fontWeight': 'normal', 'color': 'rgb(194,166,66)'}),
                                html.Table(
                                    style={'width': '100%'},
                                    children=[
                                        html.Tr([
                                            html.Td("Notional", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Equity", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Leverage", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Debt", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Free Equity", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Free Leverage", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'})
                                        ]),
                                        html.Tr([
                                            html.Td(f"{df[df['strategy'] == 'Quality']['notional'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[df['strategy'] == 'Quality']['equity'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[df['strategy'] == 'Quality']['notional'].sum() / df[df['strategy'] == 'Delta Neutral']['equity'].sum():.1f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Quality') & (df['value'] < 0)]['value'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Quality') & ~df['position_type'].isin(['vesting', 'locked'])]['equity'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Quality') & ~df['position_type'].isin(['vesting', 'locked'])]['notional'].sum() / df[(df['strategy'] == 'Quality') & ~df['position_type'].isin(['vesting', 'locked'])]['equity'].sum():.1f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'})
                                        ])
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            style={'borderLeft': '3px solid rgb(52,224,190)', 'paddingLeft': '10px', 'marginBottom': '20px'},
                            children=[
                                html.H3("Delta Neutral", style={'margin': '0', 'fontSize': '24px', 'fontWeight': 'normal', 'color': 'rgb(194,166,66)'}),
                                html.Table(
                                    style={'width': '100%'},
                                    children=[
                                        html.Tr([
                                            html.Td("Notional", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Equity", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Leverage", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Debt", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Free Equity", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Free Leverage", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'})
                                        ]),
                                        html.Tr([
                                            html.Td(f"{df[df['strategy'] == 'Delta Neutral']['notional'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[df['strategy'] == 'Delta Neutral']['equity'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[df['strategy'] == 'Delta Neutral']['notional'].sum() / df[df['strategy'] == 'Delta Neutral']['equity'].sum():.1f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Delta Neutral') & (df['value'] < 0)]['value'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Delta Neutral') & ~df['position_type'].isin(['vesting', 'locked'])]['equity'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Delta Neutral') & ~df['position_type'].isin(['vesting', 'locked'])]['notional'].sum() / df[(df['strategy'] == 'Delta Neutral') & ~df['position_type'].isin(['vesting', 'locked'])]['equity'].sum():.1f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'})
                                        ])
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            style={'borderLeft': '3px solid rgb(52,224,190)', 'paddingLeft': '10px'},
                            children=[
                                html.H3("Discretionary", style={'margin': '0', 'fontSize': '24px', 'fontWeight': 'normal', 'color': 'rgb(194,166,66)'}),
                                html.Table(
                                    style={'width': '100%'},
                                    children=[
                                        html.Tr([
                                            html.Td("Notional", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Equity", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Leverage", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Debt", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Free Equity", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td("Free Leverage", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'})
                                        ]),
                                        html.Tr([
                                            html.Td(f"{df[df['strategy'] == 'Discretionary']['notional'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[df['strategy'] == 'Discretionary']['equity'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[df['strategy'] == 'Discretionary']['notional'].sum() / df[df['strategy'] == 'Discretionary']['equity'].sum():.1f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Discretionary') & (df['value'] < 0)]['value'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Discretionary') & ~df['position_type'].isin(['vesting', 'locked'])]['equity'].sum():,.0f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'}),
                                            html.Td(f"{df[(df['strategy'] == 'Discretionary') & ~df['position_type'].isin(['vesting', 'locked'])]['notional'].sum() / df[(df['strategy'] == 'Discretionary') & ~df['position_type'].isin(['vesting', 'locked'])]['equity'].sum():.1f}", style={'padding': '1px', 'lineHeight': '1', 'textAlign': 'left', 'width': '16%'})
                                        ])
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                # Pie Charts
                html.Div(
                    style={'border': '1px solid #888888', 'padding': '13px', 'flex': '1 1 30%', 'margin': '5px', 'minWidth': '300px'},
                    children=[
                        dcc.Graph(id='equity-pie-chart', style={'width': '100%', 'height': '400px', 'marginTop': '-15px'})
                    ]
                ),
                html.Div(
                    style={'border': '1px solid #888888', 'padding': '13px', 'flex': '1 1 30%', 'margin': '5px', 'minWidth': '300px'},
                    children=[
                        dcc.Graph(id='notional-pie-chart', style={'width': '100%', 'height': '400px', 'marginTop': '-15px'})
                    ]
                )
            ]
        )
    ]
)

# Define callback to update pie chart
def update_pie_chart(_):
    if 'strategy' in df.columns and 'equity' in df.columns:
        strategy_df = df.groupby('strategy')['equity'].sum().reset_index()
        fig = px.pie(
            strategy_df,
            values='equity',
            names='strategy',
            title='Equity Allocation',
            color_discrete_sequence=['rgb(194,166,66)', 'rgb(26,57,59)', 'rgb(52,224,190)']
        )
        fig.update_layout(
            paper_bgcolor='#000000',
            font_color='#FFFFFF',
            font_family='Rajdhani',
            title_font_size=24,
            title_x=0.5,
            showlegend=False
        )
        fig.update_traces(
            textinfo='percent+label',
            textfont_size=16,
            hovertemplate='%{label}: %{percent:.2%}<extra></extra>'
        )
        return fig
    else:
        return {}

# Define callback to update notional pie chart
def update_notional_pie_chart(_):
    if 'strategy' in df.columns and 'notional' in df.columns:
        strategy_df = df.groupby('strategy')['notional'].sum().reset_index()
        fig = px.pie(
            strategy_df,
            values='notional',
            names='strategy',
            title='Notional Allocation',
            color_discrete_sequence=['rgb(194,166,66)', 'rgb(26,57,59)', 'rgb(52,224,190)']
        )
        fig.update_layout(
            paper_bgcolor='#000000',
            font_color='#FFFFFF',
            font_family='Rajdhani',
            title_font_size=24,
            title_x=0.5,
            showlegend=False
        )
        fig.update_traces(
            textinfo='percent+label',
            textfont_size=16,
            hovertemplate='%{label}: %{percent:.2%}<extra></extra>'
        )
        return fig
    else:
        return {}

# Register callbacks
def register_callbacks(app):
    app.callback(
        Output('equity-pie-chart', 'figure'),
        [Input('equity-pie-chart', 'id')]
    )(update_pie_chart)

    app.callback(
        Output('notional-pie-chart', 'figure'),
        [Input('notional-pie-chart', 'id')]
    )(update_notional_pie_chart)
