# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_minify import Minify
from sys import exit

try:
    from apps.config import config_dict
    from apps import create_app, db
    from apps.commands.create_admin import CreateAdmin
    from ftp_server import testFTPConnection
except ImportError:
    # import from dashboard
    from Dashboard.apps.config import config_dict
    from Dashboard.apps import create_app, db
    from Dashboard.apps.commands.create_admin import CreateAdmin
    from Dashboard.ftp_server import testFTPConnection



# WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'
# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
app.config['ENV'] = get_config_mode.capitalize()
Migrate(app, db)

# DB Migration
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)


@app.cli.command("create_admin")
def create_admin():
    # Make sure we have the tables
    db.create_all()
    # Create the admin user
    CreateAdmin.create_admin()


@app.cli.command("test_ftp")
def test_ftp():
    if testFTPConnection():
        app.logger.info('FTP connection OK')
    else:
        app.logger.info('FTP connection ERROR')


if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG))
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE')
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT)

def binance_bot(app_object=None):
    # Init Bot and Exchange
    from BOTs.Binance_Bot.Binance_Bot import Binance_Bot
    assert Binance_Bot.breathing == False, "Binance Bot is already breathing 🤖 ... check your code"
    from Indicators_Strategy_Handlers.Premium_Indicator_Handler import premium_indicator_function
    binance_bot_client = Binance_Bot(tradingview_bot_function=premium_indicator_function, app_object=app_object)
    # assert binance_bot_client, "Binance Bot is not breathing right after initialization was attempted 🤖"

    app = binance_bot_client.app  # for gunicorn to run the app (see Procfile)
    #
    # # Start App (begin listening) if not testing
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


if __name__ == "__main__":
    #Start the BinanceBot
    app=binance_bot(app_object=None)

    with app.app_context():
        manager.run()
