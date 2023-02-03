# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os 

class Config(object):
    
    # for Product model
    CURRENCY     = { 'usd' : 'usd' , 'eur' : 'eur' }
    STATE        = { 'completed' : 1 , 'pending' : 2, 'refunded' : 3 }
    PAYMENT_TYPE = { 'cc' : 1 , 'paypal' : 2, 'wire' : 3 }
    
    USERS_ROLES  = { 'ADMIN'  :1 , 'USER'      : 2 }
    USERS_STATUS = { 'ACTIVE' :1 , 'SUSPENDED' : 2 }
    
    # USERS_STATUS = { 'ACTIVE' :1 , 'SUSPENDED' : 2 }
    # check verified_email
    VERIFIED_EMAIL = { 'verified' :1 , 'not-verified' : 2 }

    LOGIN_ATTEMPT_LIMIT = 3

    DEFAULT_IMAGE_URL =  'static/assets/images/'

    # Read the optional FTP values
    FTP_SERVER   = os.getenv( 'FTP_SERVER'   )
    FTP_USER     = os.getenv( 'FTP_USER'     )
    FTP_PASSWORD = os.getenv( 'FTP_PASSWORD' )
    FTP_WWW_ROOT = os.getenv( 'FTP_WWW_ROOT' )

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')
    SECURITY_PASSWORD_SALT = 'f495b66803a6512d'

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')
    
    # Social AUTH Settings
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv('OAUTHLIB_INSECURE_TRANSPORT')

    SOCIAL_AUTH_GITHUB  = False
    SOCIAL_AUTH_TWITTER = False

    GITHUB_ID      = os.getenv('GITHUB_ID')
    GITHUB_SECRET  = os.getenv('GITHUB_SECRET')

    # Enable/Disable Github Social Login    
    if GITHUB_ID and GITHUB_SECRET:
         SOCIAL_AUTH_GITHUB  = True

    TWITTER_ID     = os.getenv('TWITTER_ID')
    TWITTER_SECRET = os.getenv('TWITTER_SECRET')

    # Enable/Disable Twiter Social Login
    if TWITTER_ID and TWITTER_SECRET:
         SOCIAL_AUTH_TWITTER  = True

    # Mail Settings
    MAIL_SERVER   = os.getenv('MAIL_SERVER')
    MAIL_PORT     = os.getenv('MAIL_PORT')

    # Mail Authentication
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS  = True

    # Mail Accounts
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
class ProductionConfig(Config):

    basedir = os.path.abspath(os.path.dirname(__file__))
    DEBUG = False

    # Mysql database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
          os.getenv('DB_ENGINE'   , 'mysql'),
          os.getenv('DB_USERNAME' , 'appseed_db_usr'),
          os.getenv('DB_PASS'     , 'pass'),
          os.getenv('DB_HOST'     , 'localhost'),
          os.getenv('DB_PORT'     , 3306),
          os.getenv('DB_NAME'     , 'appseed_db')
    )

class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}