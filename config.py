import os
import secrets
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

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
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 分页配置
    POSTS_PER_PAGE = 10

    # 定时任务配置
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
