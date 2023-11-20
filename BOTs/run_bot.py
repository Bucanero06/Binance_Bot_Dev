import os


def main():
    # import dotenv
    # # Load .env file
    # dotenv.load_dotenv(dotenv.find_dotenv())

    exchange_name = os.getenv("EXCHANGE")

    if exchange_name.lower() == "binance":

        # Init Bot and Exchange
        from BOTs.Binance_Bot.Binance_Bot import Binance_Bot
        assert Binance_Bot.breathing == False, "Binance Bot is already breathing 🤖 ... check your code"
        from Indicators_Strategy_Handlers.Premium_Indicator_Handler import premium_indicator_function
        binance_bot_client = Binance_Bot(tradingview_bot_function=premium_indicator_function, app_object=None, port=5000)
        # assert binance_bot_client, "Binance Bot is not breathing right after initialization was attempted 🤖"

        app = binance_bot_client.app  # for gunicorn to run the app (see Procfile)
        #
        # Start App (begin listening) if not testing
        if binance_bot_client.test_mode:
            binance_bot_client.test_binance_bot()
        else:
            # binance_bot_client.up()
            binance_bot_client.test_binance_bot()

        #
        binance_bot_client.log.info(f"Binance Bot ping {binance_bot_client.breathing} 🤖")

        if binance_bot_client.test_mode:
            # Shut down the bot if testing
            binance_bot_client.down()

        return app
    elif exchange_name.lower() == 'mexc':
        # Init Bot and Exchange
        from BOTs.MEXC_Bot.MEXC_Bot import MEXC_Bot
        assert MEXC_Bot.breathing == False, "MEXC Bot is already breathing 🤖 ... check your code"
        from BOTs.MEXC_Bot.MEXC_Premium_Indicator_Handler import premium_indicator_function
        MEXC_bot_client = MEXC_Bot(tradingview_bot_function=premium_indicator_function, app_object=None,
                                         port=5000)
        # assert MEXC_bot_client, "MEXC Bot is not breathing right after initialization was attempted 🤖"

        app = MEXC_bot_client.app  # for gunicorn to run the app (see Procfile)
        #
        # Start App (begin listening) if not testing
        if MEXC_bot_client.test_mode:
            MEXC_bot_client.test_mexc_bot()
        else:
            # MEXC_bot_client.up()
            MEXC_bot_client.test_mexc_bot()

        #
        MEXC_bot_client.log.info(f"MEXC Bot ping {MEXC_bot_client.breathing} 🤖")

        if MEXC_bot_client.test_mode:
            # Shut down the bot if testing
            MEXC_bot_client.down()

        return app


app = main()
