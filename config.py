# -*- coding: utf-8 -*-

import os
import secrets
from urllib.parse import quote

class Config:

    # 密钥配置
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(16)

    # 数据库配置
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite') # [sqlite, mysql, mariadb, postgresql]
    DB_TYPE = DB_TYPE.lower()
    if DB_TYPE in ['mysql', 'mariadb', 'postgresql']:
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '3306')
        DB_USERNAME = os.environ.get('DB_USERNAME', 'wakeonlan')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', 'pls_use_strong_password')
        DB_SCHEMA = os.environ.get('DB_SCHEMA', 'wakeonlan')
        target_database_url = f'{DB_TYPE}://{quote(DB_USERNAME)}:{quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_SCHEMA}'
    else:
        DB_SCHEMA = os.environ.get('DB_SCHEMA', 'wakeonlan')
        target_database_url = f'sqlite:///{DB_SCHEMA}.db'

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or target_database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # Limiter
    RATELIMIT_DEFAULT = "86400 per day; 3600 per hour"
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_HEADERS_ENABLED = True

    # Scheduler
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """ 开发环境 """
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """ 测试环境 """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """ 生产环境 """
    pass

class DockerConfig(ProductionConfig):
    """ Docker 环境 """

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        # log to stderr
        import logging
        from logging import StreamHandler
        handler = StreamHandler()
        handler.setLevel(logging.WARNING)
        app.logger.addHandler(handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    "docker": DockerConfig,

    # 默认环境
    'default': DevelopmentConfig
}
