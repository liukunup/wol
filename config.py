# -*- coding: utf-8 -*-

import os
import secrets
from dotenv import load_dotenv

class Config:

    # 密钥配置
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(16)

    # 数据库配置
    database_type = os.environ.get('DB_TYPE', 'sqlite') # [sqlite, mysql, mariadb, postgresql]
    database_type = database_type.lower()
    if database_type in ['mysql', 'mariadb', 'postgresql']:
        database_host = os.environ.get('DB_HOST', 'localhost')
        database_port = os.environ.get('DB_PORT', '3306')
        database_username = os.environ.get('DB_USERNAME', 'wakeonlan')
        database_password = os.environ.get('DB_PASSWORD', 'pls_set_stronger_password')
        database_name = os.environ.get('DB_NAME', 'wakeonlan')
        database_url = f'{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}'
    else:
        database_name = os.environ.get('DB_NAME', 'wakeonlan')
        database_url = f'sqlite:///{database_name}.db'

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # Limiter
    RATELIMIT_DEFAULT = "86400 per day;3600 per hour"
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
    'default': DevelopmentConfig
}
