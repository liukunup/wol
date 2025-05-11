# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from flask_apscheduler import APScheduler


class Base(DeclarativeBase):
    pass

# 数据库扩展
db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# 定时任务扩展
scheduler = APScheduler()