# -*- coding: utf-8 -*-

from flask import Flask, render_template
from config import config

def create_app(config_name='default'):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from .extensions import db, migrate
    from .main import models
    db.init_app(app)
    migrate.init_app(app, db)

    from .extensions import scheduler
    from .main import cronjobs
    scheduler.init_app(app)
    scheduler.start()

    from .extensions import limiter
    limiter.init_app(app)

    from .main import blueprint as main_blueprint
    app.register_blueprint(main_blueprint)

    # 添加应用级别的404错误处理
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error.html'), 404

    return app
