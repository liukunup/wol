# -*- coding: utf-8 -*-

"""
This file is the entry point for initializing the Flask application.
It creates a Flask application instance, configures it, 
initializes extensions, and registers blueprints.
"""

from flask import Flask
from config import config

def create_app(config_name='default'):
    # 创建 Flask 应用实例
    app = Flask(__name__)
    # 从配置对象中加载应用配置
    app.config.from_object(config[config_name])

    # 初始化扩展
    from .extensions import db, migrate, scheduler
    db.init_app(app)
    migrate.init_app(app, db)

    # 初始化定时任务
    from .main import cronjobs
    scheduler.init_app(app)
    scheduler.start()

    # 注册蓝图
    from .main import blueprint as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
