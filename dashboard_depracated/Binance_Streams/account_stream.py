binance_api_key = "316ee06e009b0ec07b92d15328bed7f0a92c7e1ddb2ce8a755273a6d4f91c802"
binance_api_secret = "e56b5fbc30dee0b4eb951933b39bc6eb4864a7ae2b60768a6697960b3ff5e838"
exchange = "binance.com-futures-testnet"

from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
import logging
import time
import threading
import os

logging.getLogger("unicorn_binance_websocket_api")
logging.basicConfig(level=logging.INFO,
                    # filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

import streamlit


def print_stream_data_from_stream_buffer(binance_websocket_api_manager):
    while True:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            # pass
            print(oldest_stream_data_from_stream_buffer)


def start_user_stream():
    # Update

    # create instances of BinanceWebSocketApiManager
    ubwa_com = BinanceWebSocketApiManager(exchange=exchange)

    # create the userData streams
    user_stream_id = ubwa_com.create_stream('arr', '!userData', api_key=binance_api_key, api_secret=binance_api_secret,
                                            output="UnicornFy")

    import streamlit as st
    def track_account_stream(stream_manager):
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        while True:
            if stream_manager.is_manager_stopping():
                exit(0)
            stream_data_point = stream_manager.pop_stream_data_from_stream_buffer()
            if not stream_data_point:
                time.sleep(0.01)
            else:
                print(stream_data_point)

                if stream_data_point['event_type'] == 'ACCOUNT_CONFIG_UPDATE':
                    print('ACCOUNT_CONFIG_UPDATE')
                    print(stream_data_point)
                    # r.hset('account_config', 'account_config', json.dumps(stream_data_point))
                elif stream_data_point['event_type'] == 'ACCOUNT_UPDATE':
                    # update positions
                    if 'positions' in stream_data_point:
                        import json
                        for pos in stream_data_point['positions']:
                            print(f'{pos["position_amount"] = }')
                            if float(pos["position_amount"]) == 0:
                                r.hdel("positions", pos["symbol"])
                            else:
                                r.hset('positions', pos['symbol'], json.dumps(pos))

                    print(f"{r.hgetall('positions') = }")
                elif stream_data_point['event_type'] == 'ORDER_TRADE_UPDATE':
                    if stream_data_point['current_order_status'] == 'NEW':
                        print('NEW')
                        print(stream_data_point)
                    elif stream_data_point['current_order_status'] == 'FILLED':
                        print('FILLED')
                        print(stream_data_point)
                    elif stream_data_point['current_order_status'] == 'CANCELED':
                        print('CANCELED')
                        print(stream_data_point)
                    elif stream_data_point['current_order_status'] == 'REJECTED':
                        print('REJECTED')
                        print(stream_data_point)
                    elif stream_data_point['current_order_status'] == 'EXPIRED':
                        print('EXPIRED')
                        print(stream_data_point)

                #

    # # Create a database to be updated with the latest data
    print("User Stream ID: ", user_stream_id)
    worker_thread = threading.Thread(target=track_account_stream, args=(ubwa_com,))
    worker_thread.start()

    # dict_database = {}
    # check_account_stream(ubwa_com, dict_database)

    # # Get all open orders
    # self.open_orders = self.exchange.fetch_open_orders("BTC/USDT", params={"recvWindow": 5000})
    # self.log.info(f"Open orders: {self.open_orders}")
    #
    # # Get all open positions
    # self.open_positions = self.exchange.fetch_positions(["BTC/USDT", "ETH/USDT"], params={"recvWindow": 5000})
    # self.log.info(f"Open positions: {self.open_positions}")
    #
    #
    # # Get all closed orders
    # self.closed_orders = self.exchange.fetch_closed_orders("BTC/USDT", params={"recvWindow": 5000})
    # self.log.info(f"Closed orders: {self.closed_orders}")
    # worker_thread.start()
    #
    # print(r.hgetall("Local Orders"))
    # # create the userData streams
