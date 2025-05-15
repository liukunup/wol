FROM python:3.12-slim
LABEL LIUKUN="liukunup@outlook.com"

# Default timezone
ARG TIMEZONE="Asia/Shanghai"
ENV TZ=${TIMEZONE}

# FLASK
ENV FLASK_APP=run.py
ENV FLASK_CONFIG=docker

# Vault
ENV VAULT_PASSWORD=pls_use_strong_password

# 数据库
ENV DB_TYPE=sqlite
ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DB_USERNAME=wakeonlan
ENV DB_PASSWORD=pls_use_strong_password
ENV DB_SCHEMA=wakeonlan

# 工作路径
WORKDIR /wol

# 环境部署
COPY app app
COPY migrations migrations
COPY run.py config.py entrypoint.sh LICENSE ./
COPY requirements requirements
RUN    python3 -m venv venv \
    && venv/bin/python3 -m pip install --upgrade pip \
    && venv/bin/pip3 install -r requirements/docker.txt \
    && chmod +x entrypoint.sh

# 端口暴露
EXPOSE 5000

# 程序入口
ENTRYPOINT ["./entrypoint.sh"]
