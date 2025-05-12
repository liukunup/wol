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
    if config_name in ['production', 'docker']:
        # 仅在生产环境中启用
        talisman.init_app(
            app,
            force_https=True,
            force_https_permanent=True,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,
            frame_options='DENY',
            content_security_policy={
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline'",
                'style-src': "'self' 'unsafe-inline'"
            }
        )

    from flask_cors import CORS
    CORS(app)

    from .main import blueprint as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
