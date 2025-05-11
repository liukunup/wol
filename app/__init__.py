# -*- coding: utf-8 -*-

from flask import Flask
from config import config

def create_app(config_name='default'):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from .extensions import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from .extensions import scheduler
    from .main import cronjobs
    scheduler.init_app(app)
    scheduler.start()

    from .extensions import limiter
    limiter.init_app(app)

    from .extensions import talisman
    talisman.init_app(app)

    from flask_cors import CORS
    CORS(app)

    from .main import blueprint as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
