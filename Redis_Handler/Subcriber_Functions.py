from unicorn_binance_websocket_api import BinanceWebSocketApiManager

from Redis_Handler.Redis_Binance_Stream_Handler import Binance_Stream_Handler

if __name__ == "__main__":
    # Set up the Binance Websocket Streams
    binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures-testnet")
    BINANCE_STREAM_INFOS = {"kline_1m": "btcusdt"}
    REDIS_URL = "redis://localhost"
    PUB_CHANNELS = ['1', '2']
    SUB_CHANNELS = ['1', '2']
    TEST_PRINT_FUNCTION = lambda stream_message, test_arg: print(
        f"stream_message: {stream_message}, test_arg: {test_arg}")
    #
    bsh = Binance_Stream_Handler(redis_url=REDIS_URL)  # Create the Binance Stream Handler
    bsh.test_stream(binance_websocket_api_manager=binance_websocket_api_manager,
                    binance_stream_infos=BINANCE_STREAM_INFOS, binance_subscriber_function=TEST_PRINT_FUNCTION,
                    binance_subscriber_function_kwargs={"test_arg": "test"}, pub_channels=PUB_CHANNELS,
                    sub_channels=SUB_CHANNELS)
