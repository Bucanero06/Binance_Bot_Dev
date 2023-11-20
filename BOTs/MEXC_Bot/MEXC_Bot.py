from BOTs.MEXC_Bot.MEXC_Orders_Handler import MEXC_Orders_Handler
from BOTs.MEXC_Bot.MEXC_Premium_Indicator_Handler import premium_indicator_function
from BOTs.MEXC_Bot.client import futures, spot
from BOTs.MEXC_Bot.debug_webhook_message import DEBUG_WEBHOOK_MESSAGE
from BOTs.shared.Application_Handler import Application_Handler
from BOTs.shared.Webhook_Handler import Webhook_Handler
from BOTs.shared.tempt_utils import ensure_bool

from time import sleep
import ccxt


class Persistent_Order_Handler(MEXC_Orders_Handler):
    """This class is used to keep track of orders that have been placed and their status, the main use during the
    execution of is to persitently check that the SL, TP, and TSL orders have been placed and are in the correct state
    after each interval for the duration of the trade. This avoids erroneous cancellation of trade management orders"""

    pass


class MEXC_Bot(Application_Handler, MEXC_Orders_Handler, Webhook_Handler):
    breathing = False

    def __init__(self, tradingview_bot_function,
                 app_object=None,
                 host='localhost', port=None,
                 # redis_url="redis://localhost",
                 ):
        '''
        BOT_TEST_MODE = True will run the application in test mode,
                        test webhook and endpoint_dict need to be provided at uptime to "up",
                        it will send a test webhook through the test client and then exit the application.
                        If SANDBOX_MODE is True then orders will be executed, otherwise they will be treated as dummies
                        to avoid erroneous order executions. Note: this is not a test mode for the exchange_client, it is a test
                        mode for the application to ensure that the webhook is being received and the endpoint is
                        functioning correctly. No execution should occur but please be careful and check the exchange_client

        BOT_TEST_MODE = False will run the application in production mode and will listen for webhooks from TradingView
                        and execute trades. In SANDBOX_MODE the only difference is that the Testnet will be used. In
                        general listens to incoming webhook (TradingView) via available endpoint of the application🚨

        BOT_TEST_MODE = 'live_test' will run the application in live mode just like test_mode = False but will not place
                        orders. In general this will listen to incoming webhook (TradingView) to any available
                        endpoint in production mode but will not place trades, similar to test_mode=True while
                        Sandbox is False, however does not care about the value of latter

        ** True if getenv("SANDBOX_MODE", default=True) else 'live_test')
        '''
        # self.redis_url = redis_url

        self.host = host
        self.port = port

        from os import getenv
        env_config = dict(
            WEBHOOK_PASSPHRASE=getenv("WEBHOOK_PASSPHRASE"),
            API_KEY=getenv("API_KEY"),
            SECRET_KEY=getenv("SECRET_KEY"),
            #
            ENABLE_RATE_LIMIT=getenv("ENABLE_RATE_LIMIT", default=True),
            EXCHANGE_TYPE=getenv("EXCHANGE_TYPE", default="future"),
            SANDBOX_MODE=getenv("SANDBOX_MODE", default=True),
            # EXCHANGE="mexc",  # do not change at this moment
            EXCHANGE=getenv("EXCHANGE", default="mexc"),

            BOT_TEST_MODE=getenv("BOT_TEST_MODE",
                                 default=True if getenv("SANDBOX_MODE", default=True) else 'live_test'),
            VERBOSE=getenv("VERBOSE", default="DEBUG"),
        )

        self.test_mode = ensure_bool(env_config["BOT_TEST_MODE"], exception_values=["live_test"])

        sandbox_mode = ensure_bool(env_config["SANDBOX_MODE"])
        assert self.test_mode in [True, False, "live_test"], "test_mode must be True, False or \"live_test\""
        assert sandbox_mode in [True, False], "sandbox_mode must be True, False"

        # Initialize All Classes
        super().__init__(application_name=__name__,

                         test_mode=bool(self.test_mode) if self.test_mode != "live_test" else False,
                         verbose=env_config["VERBOSE"],
                         app_object=app_object,

                         )

        # Prepare webhook
        self.tradingview_bot_function = tradingview_bot_function
        # Endpoints can be passed in when we move towards expand the bot but will set only for our use case for now
        #   since we are only using one endpoint for now and the user can pass their custom bot function
        self.bot_endpoints = dict(
            tradingview_webhook_handler=dict(
                rule='/tradingview_webhook_handler',
                function=self.tradingview_webhook_handler,
                methods=['POST'])
        )

        # Client
        self.log = self.app.logger
        self.add_endpoints(endpoint_info_dict=self.bot_endpoints)

        # Test Mode Handling
        if self.test_mode == True:
            if not sandbox_mode:
                self.log.warning("WARNING: test_mode is True but SANDBOX_MODE is False, this will send dummy orders "
                                 "to the live exchange_client using the debug webhook and endpoint_dict provided at uptime "
                                 "to \"up\" 🚨 🚨 🚨\n no execution should occur but please be careful 🚨 🚨 🚨")
                # self.log.exception("Dummy orders not implemented yet due to variations in API") & exit(
                #     1)  # todo: implement dummy orders

            else:
                self.log.info("test_mode is True and SANDBOX_MODE is True, this will execute orders in Test-Net using "
                              "the debug webhook and endpoint_dict provided at uptime to \"up\" 🚨")

        elif self.test_mode == False:
            self.log.info(f"test_mode is False and SANDBOX_MODE is {sandbox_mode}, this will execute "
                          f"{'Test-Net' if sandbox_mode else 'Live'} orders "
                          f" using incoming webhook (TradingView) to any available endpoint🚨")

        elif self.test_mode == "live_test":
            self.log.info("test_mode is \"live_test\" , this will listen to incoming webhook (TradingView) "
                          "to any available endpoint in production mode but will not place trades, similar to "
                          "test_mode=True while Sandbox is False, however does not care about the value of latter🚨")
            # self.log.exception("Dummy orders not implemented yet due to variations in API") & exit(
            #     1)  # todo: implement dummy orders

        # Exchange
        self.exchange_client, self.webhook_passphrase = self.initialize_exchange(env_config) # todo uncomment

        # Done
        self.breathing = True
        self.log.info("Initialized MEXC Bot 🤖")

    def initialize_exchange(self, env_config):
        """
        Initialize the exchange_client and return the exchange_client object and webhook passphrase
        :param env_config:
        :return: exchange_client, webhook_passphrase
        """

        assert env_config, "env_config is wtf ... hold on??? check env_config"

        self.pretty_print(
            data=env_config,
            log_level="DEBUG"
        )
        self._exchange_name = env_config["EXCHANGE"]
        self.exchange_type = env_config["EXCHANGE_TYPE"]
        self._sandbox_mode = env_config["SANDBOX_MODE"]
        self.verbose = env_config["VERBOSE"]
        self.enable_rate_limit = env_config["ENABLE_RATE_LIMIT"]

        try:
            webhook_passphrase = env_config["WEBHOOK_PASSPHRASE"]

            exchange_client = self.get_exchange_client()
            try:
                assert webhook_passphrase, "Add the WEBHOOK_PASSPHRASE variable to your environment variables 🚨"
                assert exchange_client.api_key, "Add the API_KEY variable to your environment variables 🚨"
                assert exchange_client.api_secret, "Add the SECRET_KEY variable to your environment variables 🚨"

            except AssertionError as e:
                self.log.error("Error during Exchange initialization: {}".format(e))
                raise e

        except Exception as e:
            self.log.info(
                f"An error here is most likely due to a missing environment variables and/or incorrect API keys 🚨")
            self.log.info(f"Error initialising bot  {e}")
            raise e

        return exchange_client, webhook_passphrase

    def get_exchange_client(self):
        import os

        if  self.exchange_type == 'future':
            exchange_client = futures.HTTP(api_key=os.getenv('API_KEY'), api_secret=os.getenv('SECRET_KEY'))
        elif self.exchange_type == 'spot':
            exchange_client = spot.HTTP(api_key=os.getenv('API_KEY'), api_secret=os.getenv('SECRET_KEY'))
        else:
            raise ValueError(f'Invalid exchange_client type: {self.exchange_type}')
        return exchange_client

    def tradingview_webhook_handler(BOT):
        """Webhook to receive TradingView signals"""
        # Accept and Prepare Webhook
        message = BOT.fetch_new_webhook()
        # return message
        # Run TradingView Webhook Handler
        # assert message["Account_Settings"]["passphrase"] == BOT.webhook_passphrase, "Incorrect passphrase" # todo uncomment
        #
        return_message = BOT.tradingview_bot_function(BOT=BOT, webhook_message=message)

        BOT.log.info("Web-Hook Return Message:")
        BOT.pretty_print(return_message)

        BOT.log.info(f"MEXC Bot ping {BOT.breathing} 🤖")

        return return_message

    def test_mexc_bot(self):
        SLEEP_BETWEEN_UPDATES = 1
        from time import perf_counter

        start = perf_counter()
        DEBUG_WEBHOOK_MESSAGE.update({'Signals': {"Buy": 1, "Minimal_Buy": 0, "Strong_Buy": 0, "Minimal_Strong_Buy": 0,
                                                  "Exit_Buy": 0, "Sell": 0, "Minimal_Sell": 0, "Strong_Sell": 0,
                                                  "Minimal_Strong_Sell": 0, "Exit_Sell": 0, "Clear_Orders": 0}})
        self.up(test_webhook_message=DEBUG_WEBHOOK_MESSAGE,
                test_endpoint_dict=self.bot_endpoints["tradingview_webhook_handler"])
        # sleep(SLEEP_BETWEEN_UPDATES)
        # DEBUG_WEBHOOK_MESSAGE.update({'Signals': {"Buy": 0, "Minimal_Buy": 0, "Strong_Buy": 0, "Minimal_Strong_Buy": 0,
        #                                           "Exit_Buy": 0, "Sell": 1, "Minimal_Sell": 0, "Strong_Sell": 0,
        #                                           "Minimal_Strong_Sell": 0, "Exit_Sell": 0, "Clear_Orders": 0}})
        # self.up(test_webhook_message=DEBUG_WEBHOOK_MESSAGE,
        #         test_endpoint_dict=self.bot_endpoints["tradingview_webhook_handler"])
        # sleep(SLEEP_BETWEEN_UPDATES)
        # DEBUG_WEBHOOK_MESSAGE.update({'Signals': {"Buy": 0, "Minimal_Buy": 0, "Strong_Buy": 0, "Minimal_Strong_Buy": 0,
        #                                           "Exit_Buy": 0, "Sell": 0, "Minimal_Sell": 0, "Strong_Sell": 0,
        #                                           "Minimal_Strong_Sell": 0, "Exit_Sell": 1, "Clear_Orders": 0}})
        # self.up(test_webhook_message=DEBUG_WEBHOOK_MESSAGE,
        #         test_endpoint_dict=self.bot_endpoints["tradingview_webhook_handler"])
        # sleep(SLEEP_BETWEEN_UPDATES)
        # DEBUG_WEBHOOK_MESSAGE.update({'Signals': {"Buy": 0, "Minimal_Buy": 0, "Strong_Buy": 0, "Minimal_Strong_Buy": 0,
        #                                           "Exit_Buy": 0, "Sell": 0, "Minimal_Sell": 0, "Strong_Sell": 0,
        #                                           "Minimal_Strong_Sell": 0, "Exit_Sell": 0, "Clear_Orders": 1}})
        # self.up(test_webhook_message=DEBUG_WEBHOOK_MESSAGE,
        #         test_endpoint_dict=self.bot_endpoints["tradingview_webhook_handler"])
        #
        self.log.info(f"Time to run {perf_counter() - start} seconds")
        #
        self.log.info(f"MEXC Bot ping {self.breathing} 🤖")


if __name__ == "__main__":
    #
    # Init Bot and Exchange
    assert MEXC_Bot.breathing == False, "MEXC Bot is already breathing 🤖 ... check your code"
    mexc_bot_client = MEXC_Bot(tradingview_bot_function=premium_indicator_function)
    # assert mexc_bot_client, "MEXC Bot is not breathing right after initialization was attempted 🤖"

    app = mexc_bot_client.app  # for gunicorn to run the app (see Procfile)
    #
    # Start App (begin listening) if not testing
    if mexc_bot_client.test_mode:
        mexc_bot_client.test_mexc_bot()
    else:
        mexc_bot_client.up()
        # mexc_bot_client.test_mexc_bot()

    #
    mexc_bot_client.log.info(f"MEXC Bot ping {mexc_bot_client.breathing} 🤖")

    if mexc_bot_client.test_mode:
        # Shut down the bot if testing
        mexc_bot_client.down()
