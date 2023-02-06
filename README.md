# UNDER HEAVY DEVELOPMENT

![moonshot_solutions_logo.png](Dashboard%2Fapps%2Fstatic%2Fassets%2Fimg%2Flogos%2Fmoonshot_solutions_logo.png)

TradingView Strategy Alert Webhook for Binance, including Heroku Procfile and requirements.txt

by - @ruben970105

![stream_summary.png](images%2Fstream_summary.png)
## Set-Up

### Environmental Variables

    **Note these need to be set as enviroment variables either through the command line, IDE, or environment provider 
    (e.g. Heroku Config)**

    Required:    
        API_KEY = YOU_API_KEY_FOR_BINANCE
        SECRET_KEY = YOUR_SECRET_KEY
        WEBHOOK_PASSPHRASE = YOUR_CUSTOM_TV_WEBHOOK_PASSPHRASE

    Optional:
        ENABLE_RATE_LIMIT = BOOL - Defaults to True (recommended)
        EXCHANGE_TYPE = "spot" or "future" - Defaults to "future"
        SANDBOX_MODE = BOOL - Defaults to True (Test-Net)
        VERBOSE = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'] - Defaults to DEBUG
        BOT_TEST_MODE = BOOL or 'live_test' - Defaults to True (Test-Net)
    
    Note on BOT_TEST_MODE:
        True -> will run the application in test mode,
                        test webhook and endpoint_dict need to be provided at uptime to "up",
                        it will send a test webhook through the test client and then exit the application.
                        If SANDBOX_MODE is True then orders will be executed, otherwise they will be treated as dummies
                        to avoid erroneous order executions. Note: this is not a test mode for the exchange, it is a test
                        mode for the application to ensure that the webhook is being received and the endpoint is
                        functioning correctly. No execution should occur but please be careful and check the exchange

        False -> will run the application in production mode and will listen for webhooks from TradingView
                        and execute trades. In SANDBOX_MODE the only difference is that the Testnet will be used. In
                        general listens to incoming webhook (TradingView) via available endpoint of the application🚨

        'live_test' -> will run the application in live mode just like test_mode = False but will not place
                        orders. In general this will listen to incoming webhook (TradingView) to any available
                        endpoint in production mode but will not place trades, similar to test_mode=True while
                        Sandbox is False, however does not care about the value of latter

        ** True if getenv("SANDBOX_MODE", default=True) else 'live_test')

    Currently Unsupported:
        EXCHANGE_NAME = **-Only Binance-**

### Hosting Options

    1. Heroku
    2. Local Machine
    3. VPS
    4. etc...

    e.g. Heroku
        
        1. Create a Heroku account
        2. Create a new app
        3. Add the environmental variables
        4. Use the CLI to push the code to Heroku 
            
            i - Download and install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-command-line).
            
            ii - If you haven't already, log in to your Heroku account and follow the prompts to create a new SSH public key.
            
                $ heroku login

            ii - Initialize a git repository in a new or existing directory
            
                $ cd my-project/
                $ git init
                $ heroku git:remote -a {app-name on heroku}
                
                For existing repositories, simply add the heroku remote
                    $ heroku git:remote -a {app-name on heroku}

            iii - Commit your code to the repository and deploy it to Heroku using Git.
            
                $ git add .
                $ git commit -am "{commit message here}"
                $ git push heroku master

            You can now change your main deploy branch from "master" to "main" for both manual and automatic deploys, 
                please follow the instructions [here](https://help.heroku.com/O0EXQZTA/how-do-i-switch-branches-from-master-to-main).

### Web-hook

    1. Create a new Web-hook/Alert on TradingView
        a) e.g. LuxAlgo Premium Indicator
            i   - Create Alert on {ASSET}
            ii  - Set Alert "Condition" to ["LuxAlgo Premium"]["Any Confirmation"]
            iii - Set Alert "Action" to "Webhook"
            iv  - Set appropriate "Expiration Time" (e.g. 1 hour, 1 month, Open-ended)
            v   - Set "Webhook URL" to your Heroku/Hosting app URL (e.g. https://your-heroku-app.herokuapp.com)
                    make sure to select the Webhook URL check box so that the alert is sent using the Webhook
            vi  - Name Alert Name (e.g. "LuxAlgo Premium") to something that is easy to identify in the logs
            vii - Message:
                    ... #todo (still being edited)
            viii - Create Alert - Congratulations you just set up your first TradingView Strategy Alert Webhook for Binance!
                    if you want other conditions to trigger alerts, repeat steps i-viii since LuxAlgo Premium Indicator
                    does not allow for custom webhooks yet. This bot is designed to be used with the LuxAlgo Premium Indicator
                    but can be used with any TradingView Strategy Alert Webhook that is sent in the correct format.
                    See the TradingView Webhook Documentation for more information on how to create a custom webhook and notify
                    the bot of your custom webhook format for entries and exits. See the "Expanding the Bot" section in this 
                    ReadMe for more.

## Debugging

### Walk-through 3rd Party Apps (# this is an old message and needs to be updated to new changes)

	Tradingview:
		1) Check the alert configurations including type, trigger, webhook address and message
		2) Check the alerts are being run on tradingview, 
		3) Check the alert messages are correctly being filled out
	Heroku:
		1) Check that the app is build and state is up
		2) Check log after an alert being triggered and look for any error signs, status changes, 
			or the contents of the webhook.
		3) Assure a response exists
		4) Reset otherwise.
		Suggestion** if you want to assure the passphrase is not the issue add something like 
		```print(f'{webhook_message = }')``` before the  if webhook_message['passphrase'] ...
		condition inside app_utils.py function  run_binance_futures(exchange, configuration, webhook_message) ...
		This way you will print out the contents of the webhook on heroku's logs prior to being processed
		
		Suggestion**  change app.run(debug=False if configuration['sandbox_mode'] else True) to app.run(debug=True) 
		if you are going to debug in a live account. This can be found in the app.py file
		
		Hint** At this point if you arent getting any log messages other than build prints even when tradingview 
		is sending signals, the focus to solve this needs to be on either tradingview creating/sending webhooks or
		heroku's listeing to the webhooks. 
	Binance:
		1)Do make sure that
			a) No trades are being placed if you arent seeing any logs on heroku
			b) The right API key is being used for the correct binance endpoint
			c) Using a test account run ccxt_test.py and change the  WEBHOOK_MESSAGE to play around with the execution
		2) Be aware of execution time, min size orders, account balance, etc ... 
			a) I included useful warning/error messages for interacting with binance, non important for this problem 
			but we should set alerts you can get notified when issues arise and we can talk about what you would want 
			done on each scenario

### Walk-through Local Machine

    (make sure to set the environmental variables)

#### Without incoming webhooks (e.g. passing dictionary)

    1) Run ccxt_test.py
    2) ... #todo (still being edited)

#### With incoming webhooks (e.g. using Post-Man)

    1) Run app.py 
    2) ... #todo (still being edited)

### Message Codes (#todo still being edited)

#### TradingView Specific

#### Hero Specific

#### Bot Specific

#### Binance Specific

### Codebase Organization (#todo just laying out the structure for now)

    ... #todo (still being edited)


## Disclaimer

This project is for informational purposes only. You should not construe this information or any other material as
legal, tax, investment, financial or other advice. Nothing contained herein constitutes a solicitation, recommendation,
endorsement or offer by us or any third party provider to buy or sell any securities or other financial instruments in
this or any other jurisdiction in which such solicitation or offer would be unlawful under the securities laws of such
jurisdiction.

***If you intend to use real money, use it at your own risk.***

Under no circumstances will we be responsible or liable for any claims, damages, losses, expenses, costs or liabilities
of any kind, including but not limited to direct or indirect damages for loss of profits.
