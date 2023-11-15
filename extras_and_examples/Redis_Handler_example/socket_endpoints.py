import json
from datetime import datetime
from threading import Event

import numpy as np
from time import sleep
from . import socketio, sock
from Redis_Handler.Redis_Binance_Stream_Handler import Binance_Stream_Handler
import redis

# BINANCE INFO
ACCOUNT_BALANCE = 1_043.93

# PUBLISHER MODEM
BINANCE_STREAM_INFOS = dict(
    stream_1=dict(
        markets=["btcusdt", "ethusdt", "ltcusdt", "adausdt", "dotusdt", "linkusdt", "xlmusdt", "trxusdt", "eosusdt"],
        channels=["kline_1m", "kline_5m", "kline_15m", "kline_30m", "kline_1h", "kline_2h", "kline_4h", "kline_6h",],
    ),
)
REDIS_URL = "redis://localhost"
PUB_CHANNELS = ['kline_1m_btcusdt']
SUB_CHANNELS = ['kline_1m_btcusdt']
TEST_PRINT_FUNCTION = lambda stream_message, test_arg: print(
    f"(Reader) Message Received: {stream_message} with {test_arg}"
)
BINANCE_SUBSCRIBER_FUNCTION_KWARGS = {"test_arg": "test"}
from unicorn_binance_websocket_api import BinanceWebSocketApiManager

bsh = Binance_Stream_Handler(redis_url=REDIS_URL)  # Create the Binance Stream Handler

event = Event()
event.clear()


@sock.route('/binance_publisher_initiate')
def binance_publisher_initiate(ws):
    event.clear()
    sleep(2)
    event.set()

    binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures-testnet")

    #
    # bsh.binance_websocket_publisher(
    #     break_event=event,
    #     channel_names=PUB_CHANNELS,
    #     binance_websocket_api_manager=binance_websocket_api_manager,
    #     binance_stream_infos=BINANCE_STREAM_INFOS,
    #     create_thread=False,
    #     daemon=True,  # Not used if create_thread=False
    # )
    r = redis.from_url(REDIS_URL)

    for key_name, ch_m_values in BINANCE_STREAM_INFOS.items():
        print(f'Registering {key_name} : {ch_m_values} Websocket Streams')
        binance_websocket_api_manager.create_stream(
            ch_m_values["channels"], ch_m_values["markets"], output="UnicornFy")


    websocket_stream_gate_bool = True
    while websocket_stream_gate_bool:
        if not event.is_set(): break

        # Middleman
        if binance_websocket_api_manager.is_manager_stopping(): websocket_stream_gate_bool = False
        #
        new_stream_data = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if new_stream_data is False:
            sleep(0.01)
        else:
            # Publish messages to the channels
            r.publish(PUB_CHANNELS[0], json.dumps(new_stream_data))
            # self._pubish_to_multiple_channels(r=r, channel_names=channel_names, message=new_stream_data)


@sock.route('/websocket_logs')
def websocket_logs(ws):
    event.wait()

    def websocket_logs(stream_message, websocket):
        # Simplify the stream message
        websocket.send(json.dumps(stream_message))

    # bsh.binance_websocket_subscriber(
    #     break_event=event,  # breakes while loop if event is not set
    #     channel_names=SUB_CHANNELS,
    #     binance_subscriber_function=websocket_logs,
    #     binance_subscriber_function_kwargs={"websocket": ws},
    #     create_thread=False,
    #     daemon=False,  # Not used if create_thread=False
    # )
    r = redis.from_url(REDIS_URL)

    with r.pubsub() as pubsub:
        pubsub.subscribe(*SUB_CHANNELS)

        while True:
            if not event.is_set(): break

            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                try:
                    websocket_logs(stream_message=message["data"].decode(),
                                   websocket=ws)
                except Exception as e:
                    print(e)


@sock.route('/todays_profits_sock')
def todays_profits_sock(ws):
    while True:
        # msg = ws.receive()
        time = datetime.now().strftime('%M:%S.%f')[3:-4]
        fake_dollar_profits = round(float(time) + np.random.randint(0, 103), 2)
        fake_perc_profits = round((fake_dollar_profits / ACCOUNT_BALANCE) * 100, 2)

        msg = {'time': time,
               'value': fake_dollar_profits,
               'value_perc': fake_perc_profits
               }
        ws.send(json.dumps(msg))

        sleep(0.2)


@sock.route('/todays_trades_sock')
def todays_trades_sock(ws):
    while True:
        # msg = ws.receive()
        time = datetime.now().strftime('%M:%S.%f')[3:-4]
        fake_dollar_profits = round(np.random.randint(1, 10), 0)
        fake_perc_profits = round((fake_dollar_profits / ACCOUNT_BALANCE) * 100, 0)

        msg = {'time': time,
               'value': fake_dollar_profits,
               'value_perc': fake_perc_profits
               }
        ws.send(json.dumps(msg))

        sleep(0.2)


@sock.route('/open_trades_sock')
def open_trades_sock(ws):
    while True:
        # msg = ws.receive()
        time = datetime.now().strftime('%M:%S.%f')[3:-4]
        fake_dollar_profits = round(float(time) + np.random.randint(0, 4), 2)
        fake_perc_profits = round((fake_dollar_profits / ACCOUNT_BALANCE) * 100, 2)

        msg = {'time': time,
               'value': fake_dollar_profits,
               'value_perc': fake_perc_profits
               }
        ws.send(json.dumps(msg))

        sleep(0.2)


@sock.route('/account_balance_sock')
def account_balance_sock(ws):
    while True:
        time = datetime.now().strftime('%M:%S.%f')[3:-4]
        fake_dollar_profits = round(ACCOUNT_BALANCE +  np.random.randint(0, 103), 2)
        fake_perc_profits = round((ACCOUNT_BALANCE + fake_dollar_profits/ACCOUNT_BALANCE) * 100, 2)

        msg = {'time': time,
               'value': fake_dollar_profits,
               'value_perc': fake_perc_profits
               }
        ws.send(json.dumps(msg))

        sleep(0.2)
