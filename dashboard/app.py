import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pages.portfolio_summary as strategic_allocation
import pages.position_summary as portfolio_detail
import pages.asset_detail as asset_detail

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Strategic Allocation Summary', href='/', style={'marginRight': '20px', 'color': '#FFFFFF'}),
        dcc.Link('Portfolio Detail', href='/portfolio-detail', style={'marginRight': '20px', 'color': '#FFFFFF'}),
        dcc.Link('Asset Detail', href='/asset-detail', style={'color': '#FFFFFF'})
    ], style={'padding': '20px', 'backgroundColor': '#000000'}),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return strategic_allocation.layout
    elif pathname == '/portfolio-detail':
        return portfolio_detail.layout
    elif pathname == '/asset-detail':
        return asset_detail.layout
    else:
        return html.Div("404: Page not found", style={'color': 'red', 'textAlign': 'center'})

# Register callbacks for each page
strategic_allocation.register_callbacks(app)
portfolio_detail.register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
