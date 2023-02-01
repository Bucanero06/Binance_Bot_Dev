# Introduction to Dash Plotly - Data Visualization in Python Tutorial
import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)





app = Dash(__name__)

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
# df = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Dash_Introduction/intro_bees.csv")
#
# df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
# df.reset_index(inplace=True)
# print(df[:5])
binance_api_key = "316ee06e009b0ec07b92d15328bed7f0a92c7e1ddb2ce8a755273a6d4f91c802"
binance_api_secret = "e56b5fbc30dee0b4eb951933b39bc6eb4864a7ae2b60768a6697960b3ff5e838"
exchange = "binance.com-futures-testnet"


from unicorn_binance_rest_api.manager import BinanceRestApiManager

ubra = BinanceRestApiManager(binance_api_key, binance_api_secret, exchange=exchange)
klines_30m = ubra.get_historical_klines("BTCUSDT", ubra.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
# print(f"klines_1m:\r\n{klines_30m}")

# Plot the data
import plotly.graph_objects as go
import pandas as pd

df = pd.DataFrame(klines_30m, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')


tradingview_source_code_path= "dashboard_depracated/widgets/tradingview_chart.html"
# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    html.Div([
        html.Iframe(
            # sandbox='allow-scripts',
            id='tradingview_chart',
            height='10000vh',
            width='100%',
            style={'border-width': '0'},
            ################ The magic happens here
            srcDoc=open(tradingview_source_code_path).read()
            ################ The magic happens here
        )
    ],
        # Style the iframe properly to automatically resize with the page),
        style={'width': '100%', 'height': '100000vh', 'overflow': 'hidden', 'padding': '0px'}
    ),


    dcc.Graph(figure=go.Figure(data=[go.Candlestick(x=df['open_time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])),


    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by user was: {}".format(option_slctd)

    dff = df.copy()
    # dff = dff[dff["Year"] == option_slctd]
    # dff = dff[dff["Affected by"] == "Varroa_mites"]
    #
    # # Plotly Express
    # fig = px.choropleth(
    #     data_frame=dff,
    #     locationmode='USA-states',
    #     locations='state_code',
    #     scope="usa",
    #     color='Pct of Colonies Impacted',
    #     hover_data=['State', 'Pct of Colonies Impacted'],
    #     color_continuous_scale=px.colors.sequential.YlOrRd,
    #     labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
    #     template='plotly_dark'
    # )

    # Plotly Graph Objects (GO)
    fig = go.Figure(data=[go.Candlestick(x=df['open_time'],
                    open=df['open'], high=df['high'],
                    low=df['low'], close=df['close'])])

    # fig = go.Figure(
    #     data=[go.Choropleth(
    #         locationmode='USA-states',
    #         locations=dff['state_code'],
    #         z=dff["Pct of Colonies Impacted"].astype(float),
    #         colorscale='Reds',
    #     )]
    # )
    #
    # fig.update_layout(
    #     title_text="Bees Affected by Mites in the USA",
    #     title_xanchor="center",
    #     title_font=dict(size=24),
    #     title_x=0.5,
    #     geo=dict(scope='usa'),
    # )

    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)