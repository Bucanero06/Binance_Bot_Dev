# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import threading
from datetime import datetime

from flask_minify import Minify
###
import redis
from Dashboard import app, sock

###
HOST = 'localhost'
PORT = 6379
DEBUG = app.config['DEBUG']

###
r = redis.Redis(host=HOST, port=PORT)
app.config["REDIS_URL"] = f"redis://{HOST}:{PORT}"

# r = redis.Redis(app)

###

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

app.logger.info('DEBUG            = ' + str(DEBUG))
app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE')
app.logger.info('ASSETS_ROOT      = ' + app.config['ASSETS_ROOT'])

if __name__ == "__main__":
    app.run()
