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

    # 仅在非生产环境中自动执行建表和迁移
    # 建议在生产环境中手动执行`flask db upgrade`
    if config_name not in ['production', 'docker']:
        with app.app_context():
            db.create_all()
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

    # 添加应用级别的404错误处理
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error.html'), 404

    return app
