import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import yfinance as yf
import plotly.express as px
import pandas as pd
import datetime

app = dash.Dash(__name__)
app.title = "📈 Stock & Crypto Analytics Dashboard"

# Global dark theme styles
app.layout = html.Div([
    html.H1("📈 Stock & Crypto Analytics Dashboard",
            style={'textAlign': 'center', 'color': 'white'}),

    html.Div([
        html.Label("Enter Ticker Symbol:", style={'color': 'white'}),
        dcc.Input(id='ticker', value='AAPL', type='text', style={'backgroundColor': '#222', 'color': 'white'}),

        html.Label("Start Date:", style={'color': 'white'}),
        dcc.DatePickerSingle(id='start', date='2023-01-01'),

        html.Label("End Date:", style={'color': 'white'}),
        dcc.DatePickerSingle(id='end', date=pd.Timestamp.today())
    ], style={
        'display': 'grid',
        'grid-template-columns': '1fr 1fr 1fr',
        'gap': '10px',
        'color': 'white'
    }),

    html.Br(),

    dcc.Graph(id='price-chart'),
    dcc.Graph(id='volume-chart'),
    dcc.Graph(id='returns-chart'),
    dcc.Graph(id='heatmap-chart')
], style={'backgroundColor': '#000', 'padding': '20px', 'minHeight': '100vh'})

@app.callback(
    [Output('price-chart', 'figure'),
     Output('volume-chart', 'figure'),
     Output('returns-chart', 'figure'),
     Output('heatmap-chart', 'figure')],
    [Input('ticker', 'value'),
     Input('start', 'date'),
     Input('end', 'date')]
)
def update_dashboard(ticker, start, end):
    start = pd.to_datetime(start).date() if start else datetime.date(2023, 1, 1)
    end = pd.to_datetime(end).date() if end else datetime.date.today()

    data = yf.download(ticker, start=start, end=end, auto_adjust=False)

    if data.empty:
        # Handle invalid ticker or no data
        fig = px.scatter(title="No data available", template="plotly_dark")
        return [fig, fig, fig, fig]

    # Flatten multi-index columns if any
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]

    # Compute daily returns
    data['Daily Return'] = data['Adj Close'].pct_change()

    # --- Chart 1: Price Line ---
    fig1 = px.line(data, x=data.index, y='Adj Close', title=f'{ticker} Closing Price', template='plotly_dark')

    # --- Chart 2: Volume ---
    fig2 = px.bar(data, x=data.index, y='Volume', title='Volume Traded', template='plotly_dark')

    # --- Chart 3: Daily Returns Histogram ---
    fig3 = px.histogram(data, x='Daily Return', nbins=50, title='Return Distribution', template='plotly_dark')

    # --- Chart 4: Heatmap (Correlation Matrix) ---
    corr_data = data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Daily Return']].corr()
    fig4 = px.imshow(
        corr_data,
        text_auto=True,
        color_continuous_scale='portland',
        title='Feature Correlation Heatmap',
        template='plotly_dark'
    )

    return fig1, fig2, fig3, fig4


if __name__ == '__main__':
    app.run(debug=True, port=8051)
