import json
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from unicorn_binance_local_depth_cache import DepthCacheOutOfSync
from unicorn_binance_rest_api.manager import BinanceRestApiManager

from dashboard_depracated.Binance_Streams.account_stream import start_user_stream
from dashboard_depracated.webhook_configuration.render_configuration_form import render_binance_bot_configuration_form
import unicorn_binance_local_depth_cache

from dashboard_depracated.webhook_configuration.render_configuration_table import render_configuration_table
import redis

# Sidebar
st.sidebar.title("Binance Futures Scratch Dashboard demo (Testnet)")

binance_api_key = "316ee06e009b0ec07b92d15328bed7f0a92c7e1ddb2ce8a755273a6d4f91c802"
binance_api_secret = "e56b5fbc30dee0b4eb951933b39bc6eb4864a7ae2b60768a6697960b3ff5e838"
exchange_futures_testnet = "binance.com-futures-testnet"
exchange_com_testnet = "binance.com-futures-testnet"

ORDER_DEPTH_ON = False
ORDER_HISTORY_ON = True
# add configuration button which pops up a configuration form


dropdown = st.sidebar.selectbox("Select Configuration",
                                ["Overview", "Bot Control", "Create New Configuration", "View Existing Configuration"])

start_user_stream()

def update_datastreams():
    ...


if dropdown == "Overview":
    pass

if dropdown == "Bot Control":
    placeholder = st.empty()
    ubra = BinanceRestApiManager(binance_api_key, binance_api_secret, exchange=exchange_futures_testnet, )

    with placeholder.container():
        if ORDER_DEPTH_ON == True:
            ubldc = unicorn_binance_local_depth_cache.BinanceLocalDepthCacheManager(exchange=exchange_com_testnet)
            ubldc.create_depth_cache("BTCUSDT")
        ###########################################################
        if ORDER_DEPTH_ON == True:
            if ubldc.is_depth_cache_synchronized("BTCUSDT"):
                try:
                    bids = ubldc.get_bids(market='BTCUSDT')[:10]
                    asks = ubldc.get_asks(market='BTCUSDT')[:10]

                    # Convert to orderbook visualisation format (bid/ask, price, quantity)
                    bids = pd.DataFrame(bids, columns=["Bid Price", "Bid Quantity"])
                    bids.columns = ["Bid Quantity", "Bid Price"]
                    asks = pd.DataFrame(asks, columns=["Ask Price", "Ask Quantity"])
                    order_book = pd.concat([bids, asks], axis=1)
                    st.dataframe(order_book, width=420, height=240)

                except Exception as error_msg:
                    st.write(f"ERROR: {error_msg}")

        if ORDER_HISTORY_ON == True:
            # get positions
            st.markdown(f'orderHistory')
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            positions = redis_client.hgetall('positions')
            st.markdown(f'positions: {positions}')




elif dropdown == "Create New Configuration":
    render_binance_bot_configuration_form(configuration_database_name="webhook_asset_configurations")

elif dropdown == "View Existing Configuration":
    render_configuration_table(configuration_database_name="webhook_asset_configurations")
