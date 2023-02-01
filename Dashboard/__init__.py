# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

# import Flask 
from flask import Flask
from flask_sock import Sock

from .config import Config

# Inject Flask magic
app = Flask(__name__)

# load Configuration
app.config.from_object(Config)

# Initialize Sock
sock = Sock(app)

# Import routing to render the pages
from . import views