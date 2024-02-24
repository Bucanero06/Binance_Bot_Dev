# Stream-Bot (DEPRECATED, check AntBot) 
(readme.md is still being edited to account for breaking changes in ccxt as well as the mexc migration thus beware of deprecated codebase and instructions)

Premium **TradingView-Binance Dashboard** with Webhook/Live-Stream/API support, includes Heroku Procfile and
requirements.txt, easy to execute ReadMe Commands for easy manual set up without getting your hands dirty with the
terminal or a docker image to get you up and ready in seconds not minutes.


## 3rd Party App Support

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

## Disclaimer

This project is for informational purposes only. You should not construe this information or any other material as
legal, tax, investment, financial or other advice. Nothing contained herein constitutes a solicitation, recommendation,
endorsement or offer by us or any third party provider to buy or sell any securities or other financial instruments in
this or any other jurisdiction in which such solicitation or offer would be unlawful under the securities laws of such
jurisdiction.

***If you intend to use real money, use it at your own risk.***

Under no circumstances will we be responsible or liable for any claims, damages, losses, expenses, costs or liabilities
of any kind, including but not limited to direct or indirect damages for loss of profits.
