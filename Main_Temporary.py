import asyncio
from threading import Event

import redis.asyncio as redis
from unicorn_binance_websocket_api import BinanceWebSocketApiManager

from BOTs.Binance_Bot_Original.Binance_Bot import Binance_Bot
from Redis_Handler.Redis_Binance_Stream_Handler import Binance_Stream_Handler

# Set up the Binance Websocket Streams
binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures-testnet")
BINANCE_STREAM_INFOS = {"kline_1m": "btcusdt"}
REDIS_URL = "redis://localhost"
PUB_CHANNELS = ['kline_1m_btcusdt']
SUB_CHANNELS = ['kline_1m_btcusdt']
TEST_PRINT_FUNCTION = lambda stream_message, test_arg: print(f"stream_message: {stream_message}, test_arg: {test_arg}")
binance_subscriber_function_kwargs = {"test_arg": "test"}
#
bsh = Binance_Stream_Handler(redis_url=REDIS_URL)  # Create the Binance Stream Handler


def publisher():
    return bsh.binance_websocket_publisher(
        channel_names=PUB_CHANNELS,
        binance_websocket_api_manager=binance_websocket_api_manager,
        binance_stream_infos=BINANCE_STREAM_INFOS,
        create_thread=True,
        daemon=True,
    )


def test_function(stream_message, test_arg):
    # print(f"stream_message: {stream_message}")
    pass

def subscriber():
    return bsh.binance_websocket_subscriber(
        channel_names=SUB_CHANNELS,
        binance_subscriber_function=test_function,
        binance_subscriber_function_kwargs=binance_subscriber_function_kwargs,
        create_thread=True,
        daemon=True,


    )


# Set-Up Bitcoin Bot and Run!
# Init Bot and Exchange
def start_binance_bot():
    assert Binance_Bot.breathing == False, "Binance Bot is already breathing 🤖 ... check your code"
    from Indicators_Strategy_Handlers.Premium_Indicator_Handler import premium_indicator_function
    binance_bot_client = Binance_Bot(tradingview_bot_function=premium_indicator_function)
    # assert binance_bot_client, "Binance Bot is not breathing right after initialization was attempted 🤖"

    app = binance_bot_client.app  # for gunicorn to run the app (see Procfile)
    #
    # Start App (begin listening) if not testing
    if binance_bot_client.test_mode:
        binance_bot_client.test_binance_bot()
    else:
        binance_bot_client.up()
    #
    binance_bot_client.log.info(f"Binance Bot ping {binance_bot_client.breathing} 🤖")

    if binance_bot_client.test_mode:
        # Shut down the bot if testing
        binance_bot_client.down()

    return binance_bot_client


publisher_thread = publisher()
subscriber_thread = subscriber()
print("hello world")
event=Event()

print(f'{event.is_set() = }')
event.set()
print(f'{event.is_set() = }')
exit()
start_binance_bot()

# results = bsh.run_coroutines(coroutines=[
#     bsh.binance_websocket_publisher(
#         channel_names=PUB_CHANNELS,
#         binance_websocket_api_manager=binance_websocket_api_manager,
#         binance_stream_infos=BINANCE_STREAM_INFOS,
#     ),
#     # bbot()
#     # test_sub()
# start_binance_bot()
#     # bsh.binance_websocket_subscriber(channel_names=SUB_CHANNELS, redis_url=REDIS_URL,
#     #                                  binance_subscriber_function=TEST_PRINT_FUNCTION,
#     #                                  binance_subscriber_function_kwargs=binance_subscriber_function_kwargs
#     #                                  )
# ])
# print(results)
print("hello world")
exit()
