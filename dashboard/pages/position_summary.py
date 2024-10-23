from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px

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
            style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px', 'width': '100%'},
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
                    className='dropdown',
                    style={'flex': '1', 'marginRight': '10px'}  # Allow the dropdown to grow
                ),
                # Metrics Boxes
                html.Div(
                    id='metrics-boxes',
                    style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 'flex': '5'},
                    children=[]
                )
            ]
        ),
        # Bar Charts Container
        html.Div(
            style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 'marginTop': '20px'},
            children=[
                dcc.Graph(
                    id='notional-bar-chart',
                    config={'displayModeBar': False},
                    style={'flex': '1 1 45%', 'minWidth': '300px'}  # Allow the graph to grow and shrink
                ),
                html.Div(style={'width': '20px'}),  # Small gap between the charts
                dcc.Graph(
                    id='equity-bar-chart',
                    config={'displayModeBar': False},
                    style={'flex': '1 1 45%', 'minWidth': '300px'}  # Allow the graph to grow and shrink
                )
            ]
        ),
        # Treemap Container
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '20px'},
            children=[
                dcc.Graph(
                    id='portfolio-treemap',
                    config={'displayModeBar': False},
                    style={'flex': '1 1 100%', 'maxWidth': '800px'}  # Allow the graph to grow and shrink
                )
            ]
        )
    ]
)

# Callback to update the metrics and charts based on the selected strategy
@callback(
    [Output('metrics-boxes', 'children'),
     Output('notional-bar-chart', 'figure'),
     Output('equity-bar-chart', 'figure'),
     Output('portfolio-treemap', 'figure')],
    [Input('strategy-dropdown', 'value')]
)
def update_metrics_and_charts(selected_strategy):
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

    # Aggregate and sort data for notional by position
    aggregated_notional_df = filtered_df.groupby('position', as_index=False).agg({'notional': 'sum'})

    # Identify and group small positions into 'Other' for notional
    threshold_notional = 0.0025 * total_notional_value  # 0.25% of total notional value
    small_positions_notional = aggregated_notional_df[aggregated_notional_df['notional'] < threshold_notional]
    other_notional = small_positions_notional['notional'].sum()
    aggregated_notional_df = aggregated_notional_df[aggregated_notional_df['notional'] >= threshold_notional]

    # Create a DataFrame for the 'Other' category for notional
    other_notional_df = pd.DataFrame({'position': ['Other'], 'notional': [other_notional]})

    # Concatenate the 'Other' category with the main DataFrame for notional
    aggregated_notional_df = pd.concat([aggregated_notional_df, other_notional_df], ignore_index=True)

    # Sort by ascending order for notional
    aggregated_notional_df = aggregated_notional_df.sort_values(by='notional', ascending=True)

    # Create notional bar chart
    notional_fig = px.bar(
        aggregated_notional_df,
        x='notional',
        y='position',
        orientation='h',
        title='Notional Value by Position',
        template='plotly_dark',
        category_orders={'position': aggregated_notional_df['position'].tolist()}  # Ensure correct order
    )
    notional_fig.update_traces(marker_color='rgb(194,166,66)')  # Gold color

    # Aggregate and sort data for equity by position
    aggregated_equity_df = filtered_df.groupby('position', as_index=False).agg({'equity': 'sum'})

    # Identify and group small positions into 'Other' for equity
    threshold_equity = 0.0025 * total_equity_value  # 0.25% of total equity value
    small_positions_equity = aggregated_equity_df[aggregated_equity_df['equity'] < threshold_equity]
    other_equity = small_positions_equity['equity'].sum()
    aggregated_equity_df = aggregated_equity_df[aggregated_equity_df['equity'] >= threshold_equity]

    # Create a DataFrame for the 'Other' category for equity
    other_equity_df = pd.DataFrame({'position': ['Other'], 'equity': [other_equity]})

    # Concatenate the 'Other' category with the main DataFrame for equity
    aggregated_equity_df = pd.concat([aggregated_equity_df, other_equity_df], ignore_index=True)

    # Sort by ascending order for equity
    aggregated_equity_df = aggregated_equity_df.sort_values(by='equity', ascending=True)

    # Create equity bar chart
    equity_fig = px.bar(
        aggregated_equity_df,
        x='equity',
        y='position',
        orientation='h',
        title='Equity Value by Position',
        template='plotly_dark',
        category_orders={'position': aggregated_equity_df['position'].tolist()}  # Ensure correct order
    )
    equity_fig.update_traces(marker_color='rgb(52,224,190)')  # Teal color

    # Create a treemap with specified discrete colors
    treemap_fig = px.treemap(
        filtered_df,
        path=[px.Constant("All"), 'position', 'protocol', 'base_asset'],  # Add a constant root node
        values='notional',  # Use 'notional' for the size of the blocks
        color='position',  # Use 'position' to assign colors
        color_discrete_sequence=['rgb(194,166,66)', 'rgb(26,57,59)', 'rgb(52,224,190)'],  # Dark green, gold, teal
        title='Notional Value (All > Position > Protocol > Symbol)',
        template='plotly_dark'
    )

    # Update layout to remove padding/margins
    treemap_fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),  # Adjust margins to remove extra space
        title_x=0.5  # Center the title
    )

    # Return the updated boxes and figures
    return [
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
    ], notional_fig, equity_fig, treemap_fig

# Register the callback
def register_callbacks(app):
    app.callback(
        [Output('metrics-boxes', 'children'),
         Output('notional-bar-chart', 'figure'),
         Output('equity-bar-chart', 'figure'),
         Output('portfolio-treemap', 'figure')],
        [Input('strategy-dropdown', 'value')]
    )(update_metrics_and_charts)
