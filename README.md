#           Stream-Bot

![moonshot_solutions_logo.png](Dashboard%2Fapps%2Fstatic%2Fassets%2Fimg%2Flogos%2Fmoonshot_solutions_logo.png)

Premium **TradingView-Binance Dashboard** with Webhook/Live-Stream/API support, includes Heroku Procfile and
requirements.txt, easy to execute ReadMe Commands for easy manual set up or a docker image to get you up and ready in
seconds not minutes. Brought you by - [@Bucanero06](https://github.com/Bucanero06), Copyright (c) 2022 -
present [Moonshot Solutions](moonshot.codes)

<br />

> Features

- `Up-to-date dependencies`, active versioning
- `DB Tools`: SQLAlchemy ORM, `Flask-Migrate` (schema migrations)
- `Persistence`:
    - `SQLite` for development - `DEBUG=True` in `.env`
    - `MySql` for production - `DEBUG=False` in `.env`
- `Authentication`
    - Session Based (via **flask_login**)
    - Social Login (optional) for Github & Twitter
    - Automatic suspension on failed logins
- `Users Management`
    - `Extended user profile`
    - Complete Users management (for `Admins`)
- `API` via Flask-RestX
    - Path: `/api/`
    - `Products`, `Sales` Models
- `Message-Bus` via Redis PUB/SUB and Stream Channels
    - `Linear Scaling of ops/sec`
    - Fast and linear scaling for high production rate and easy adapt to consumer needs asynchronously and in real time
    - Fail-safe consumption, meaning automatic reconnection when failure and without any data loss
    - Redis Enterprise has been benchmarked to demonstrate true linear scaling—going from 10M ops/sec with 6 AWS EC2
      instances to 30M ops/sec with 18 AWS EC2 instances. It provides multiple ways to scale your database leading to a
      persistent, high availability and high throughput and the ability to store/process millions of stream per second
      with sub-millisecond latency
    - `Local` clusters vary
- `Deployment`
    - `Docker`
    - Page Compression via `Flask-Minify` (for production)

<br />

![Screenshot from 2023-02-03 13-42-21.png](..%2F..%2FPictures%2FScreenshots%2FScreenshot%20from%202023-02-03%2013-42-21.png)
![Screenshot from 2023-02-03 13-41-31.png](..%2F..%2FPictures%2FScreenshots%2FScreenshot%20from%202023-02-03%2013-41-31.png)
![websocket_streams_summary_example.png](Dashboard%2Fapps%2Fstatic%2Fassets%2Fimg%2Fillustrations%2Fwebsocket_streams_summary_example.png)

<br />

## ✨ Set-up

### ✨ Start the app in Docker

> **Step 1** - Download and unzip the sources

```bash
$ # Get the code
$ unzip flask-soft-ui-dashboard-enh.zip
$ cd flask-soft-ui-dashboard-enh
```

<br />

> **Step 2** - Start the APP in `Docker`

```bash
$ docker-compose up --build 
```

Visit `http://localhost:5085` in your browser. The app should be up & running.

<br />

### ✨ Create a new `.env` file using sample `env.sample`

The meaning of each variable can be found below:

- `DEBUG`: if `True` the SQLite persistence is used.
    - For production use `False` = this will switch to MySql persistence
- Flask `environment variables` (used in development)
    - `FLASK_APP=run.py`
    - `FLASK_ENV=development`
- `ASSETS_ROOT`: used in assets management
    - default value: `/static/assets`
- `MYSQL` credentials (when DEBUG=`False`)
    - `DB_ENGINE`, default value = `mysql`
    - `DB_NAME`, default value = `application_db`
    - `DB_HOST`, default value = `localhost`
    - `DB_PORT`, default value = `3306`
    - `DB_USERNAME`, default value = `application_db_usr`
    - `DB_PASS`, default value = `pass`
- `SOCIAL AUTH` Github (optional)
    - `GITHUB_ID`=YOUR_GITHUB_ID
    - `GITHUB_SECRET`=YOUR_GITHUB_SECRET
- `SOCIAL AUTH` TWITTER (optional)
    - `TWITTER_ID`=YOUR_TWITTER_ID
    - `TWITTER_SECRET`=YOUR_TWITTER_SECRET
- `BINANCE BOT` env variables (used in development and temporarily in production, moving to db)
    - `Required:`
        - `API_KEY` = YOU_API_KEY_FOR_BINANCE
        - `SECRET_KEY` = YOUR_SECRET_KEY
        - `WEBHOOK_PASSPHRASE` = YOUR_CUSTOM_TV_WEBHOOK_PASSPHRASE
    - `Optional`:
        - `ENABLE_RATE_LIMIT` = BOOL - Defaults to True (recommended)
        - `EXCHANGE_TYPE` = "spot" or "future" - Defaults to "future"
        - `SANDBOX_MODE` = BOOL - Defaults to True (Test-Net)
        - `VERBOSE` = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'] - Defaults to DEBUG
        - `BOT_TEST_MODE` = BOOL or 'live_test' - Defaults to True (Test-Net)
    - `Note on BOT_TEST_MODE:`
      `True` -> will run the application in test mode,
      test webhook and endpoint_dict need to be provided at uptime to "up",
      it will send a test webhook through the test client and then exit the application.
      If SANDBOX_MODE is True then orders will be executed, otherwise they will be treated as dummies
      to avoid erroneous order executions. Note: this is not a test mode for the exchange, it is a test
      mode for the application to ensure that the webhook is being received and the endpoint is
      functioning correctly. No execution should occur but please be careful and check the exchange

      `False` -> will run the application in production mode and will listen for webhooks from TradingView
      and execute trades. In SANDBOX_MODE the only difference is that the Testnet will be used. In
      general listens to incoming webhook (TradingView) via available endpoint of the application🚨

      `'live_test'` -> will run the application in live mode just like test_mode = False but will not place
      orders. In general this will listen to incoming webhook (TradingView) to any available
      endpoint in production mode but will not place trades, similar to test_mode=True while
      Sandbox is False, however does not care about the value of latter

      `** True if getenv("SANDBOX_MODE", default=True) else 'live_test')`

  `Currently Unsupported:`
  `EXCHANGE_NAME` = **->Only Binance<-**

<br />

### ✨ Set up the MySql Database

**Note:** Make sure your Mysql server is properly installed and accessible.

> **Step 1** - Create the MySql Database to be used by the app

- `Create a new MySql` database
- `Create a new user` and assign full privilegies (read/write)

<br />

> **Step 2** - Edit the `.env` to match your MySql DB credentials. Make sure `DB_ENGINE` is set to `mysql`.

- `DB_ENGINE`  : `mysql`
- `DB_NAME`    : default value = `application_db`
- `DB_HOST`    : default value = `localhost`
- `DB_PORT`    : default value = `3306`
- `DB_USERNAME`: default value = `application_db_usr`
- `DB_PASS`    : default value = `pass`

<br />

Here is a sample:

```txt
# .env sample

DEBUG=False                # False enables the MySql Persistence

DB_ENGINE=mysql            # Database Driver
DB_NAME=application_db         # Database Name
DB_USERNAME=application_db_usr # Database User
DB_PASS=STRONG_PASS_HERE   # Password 
DB_HOST=localhost          # Database HOST, default is localhost 
DB_PORT=3306               # MySql port, default = 3306 
```

<br />

### ✨ Manual Build

> - Download the [code](https://linkhere) and unzip the sources.

```bash
$ unzip flask-soft-ui-dashboard-enh.zip
$ cd flask-soft-ui-dashboard-enh
```

<br />

#### 👉 Set Up for `Unix`, `MacOS`

> Install modules via `VENV`

```bash
$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements_deprecated.txt
```

<br />

> Set Up Flask Environment

```bash
$ export FLASK_APP=run.py
$ export FLASK_ENV=development
```

<br />

> Set Up Database

```bash
# Init migration folder
$ flask db init # to be executed only once         
```

```bash
$ flask db migrate # Generate migration SQL
$ flask db upgrade # Apply changes
```

<br />

> Create super admin

```bash
$ flask create_admin
```

<br />

> Start the app

```bash
$ flask run
```

or

```bash
$ flask run --cert=adhoc # For HTTPS server
```

At this point, the app runs at `http://127.0.0.1:5000/`.

<br />

#### 👉 Set Up for `Windows`

> Install modules via `VENV` (windows)

```
$ virtualenv env
$ .\env\Scripts\activate
$ pip3 install -r requirements.txt
```

<br />

> Set Up Flask Environment

```bash
// CMD 
$ set FLASK_APP=run.py
$ set FLASK_ENV=development
```

or

```bash
// Powershell
$ $env:FLASK_APP = ".\run.py"
$ $env:FLASK_ENV = "development"
```

<br />

> Start the app

```bash
$ flask run
```

or

```bash
$ flask run --cert=adhoc # For HTTPS server
```

At this point, the app runs at `http://127.0.0.1:5000/`.

<br />

### 👉 Create (ordinary) Users

By default, the app redirects guest users to authenticate. In order to access the private pages, follow this set up:

- Start the app via `flask run`
- Access the `registration` page and create a new user:
    - `http://127.0.0.1:5000/register`
- Access the `sign in` page and authenticate
    - `http://127.0.0.1:5000/login`

<br />

### ✨ Code-base structure

The project is coded using blueprints, app factory pattern, dual configuration profile (development and production) and
an intuitive structure presented bellow:

```
< PROJECT ROOT >
   |
   |-- apps/
   |    |
   |    |-- home/                           # A simple app that serve HTML files
   |    |    |-- routes.py                  # Define app routes
   |    |
   |    |-- authentication/                 # Handles auth routes (login and register)
   |    |    |-- routes.py                  # Define authentication routes  
   |    |    |-- models.py                  # Defines models  
   |    |    |-- forms.py                   # Define auth forms (login and register) 
   |    |
   |    |-- static/
   |    |    |-- <css, JS, images>          # CSS files, Javascripts files
   |    |
   |    |-- templates/                      # Templates used to render pages
   |    |    |-- includes/                  # HTML chunks and components
   |    |    |    |-- navigation.html       # Top menu component
   |    |    |    |-- sidebar.html          # Sidebar component
   |    |    |    |-- footer.html           # App Footer
   |    |    |    |-- scripts.html          # Scripts common to all pages
   |    |    |
   |    |    |-- layouts/                   # Master pages
   |    |    |    |-- base-fullscreen.html  # Used by Authentication pages
   |    |    |    |-- base.html             # Used by common pages
   |    |    |
   |    |    |-- accounts/                  # Authentication pages
   |    |    |    |-- login.html            # Login page
   |    |    |    |-- register.html         # Register page
   |    |    |
   |    |    |-- home/                      # UI Kit Pages
   |    |         |-- index.html            # Index page
   |    |         |-- 404-page.html         # 404 page
   |    |         |-- *.html                # All other pages
   |    |    
   |  config.py                             # Set up the app
   |    __init__.py                         # Initialize the app
   |
   |-- requirements_deprecated.txt                     # App Dependencies
   |
   |-- .env                                 # Inject Configuration via Environment
   |-- run.py                               # Start the app - WSGI gateway
   |
   |-- ************************************************************************
```

<br />

---

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
