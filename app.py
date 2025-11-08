import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import yfinance as yf
import plotly.express as px
import pandas as pd
import datetime

app = dash.Dash(__name__)
app.title = "📈 Stock & Crypto Analytics Dashboard"

app.layout = html.Div([
    html.H1("📈 Stock & Crypto Analytics Dashboard"),

    html.Div([
        html.Label("Enter Ticker Symbol:"),
        dcc.Input(id='ticker', value='AAPL', type='text'),
        html.Label("Start Date:"),
        dcc.DatePickerSingle(id='start', date='2023-01-01'),
        html.Label("End Date:"),
        dcc.DatePickerSingle(id='end', date=pd.Timestamp.today())
    ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr 1fr', 'gap': '10px'}),

    html.Br(),

    dcc.Graph(id='price-chart'),
    dcc.Graph(id='volume-chart'),
    dcc.Graph(id='returns-chart')
])

@app.callback(
    [Output('price-chart', 'figure'),
     Output('volume-chart', 'figure'),
     Output('returns-chart', 'figure')],
    [Input('ticker', 'value'),
     Input('start', 'date'),
     Input('end', 'date')]
)
def update_dashboard(ticker, start, end):
    start = pd.to_datetime(start).date() if start else datetime.date(2023, 1, 1)
    end = pd.to_datetime(end).date() if end else datetime.date.today()

    data = yf.download(ticker, start=start, end=end, auto_adjust=False)

    if data.empty:
        return px.line(title="No Data"), px.bar(title="No Data"), px.histogram(title="No Data")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]

    data['Daily Return'] = data['Adj Close'].pct_change()

    fig1 = px.line(data, x=data.index, y='Adj Close', title=f'{ticker} Closing Price')
    fig2 = px.bar(data, x=data.index, y='Volume', title='Volume Traded')
    fig3 = px.histogram(data, x='Daily Return', nbins=50, title='Return Distribution')

    return fig1, fig2, fig3

if __name__ == '__main__':
    app.run(debug=True, port=8051)
