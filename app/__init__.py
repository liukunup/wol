from flask import Flask
from config import config

def create_app(config_name='default'):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    from .extensions import db
    db.init_app(app)

    # 注册蓝图
    from .main import blueprint as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
