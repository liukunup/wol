# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from flask_apscheduler import APScheduler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman


class Base(DeclarativeBase):
    pass

# 数据库
db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# 定时任务
scheduler = APScheduler()

# 限流
limiter = Limiter(key_func=get_remote_address)

# 安全
talisman = Talisman()