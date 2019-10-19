import os
from datetime import timedelta


class DevelopmentConfig:

    DEBUG = True
    JSON_AS_ASCII = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'lxqhpojp9usaxlksax89')

    db_user = os.getenv('CLOUD_SQL_USERNAME', 'root')
    db_password = os.getenv('CLOUD_SQL_PASSWORD', '')
    db_name = os.getenv('CLOUD_SQL_DATABASE_NAME', None)
    db_connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME', None)

    # SQLAlchemy

    # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    if os.getenv('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@/{}?unix_socket={}'.format(
            db_user, db_password, db_name, unix_socket)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8'.format(
            db_user, db_password, host, db_name)

    SQLALCHEMY_POOL_RECYCLE = 90
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 3,
    }

Config = DevelopmentConfig