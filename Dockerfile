# 基础镜像
FROM python:3.12-slim
# 作者信息
LABEL LIUKUN="liukunup@outlook.com"

# 默认时区
ARG TIMEZONE="Asia/Shanghai"
ENV TZ ${TIMEZONE}

# FLASK框架配置
ENV FLASK_APP run.py
ENV FLASK_CONFIG docker

# 数据库配置
ENV DB_TYPE sqlite
ENV DB_HOST localhost
ENV DB_PORT 3306
ENV DB_USERNAME wakeonlan
ENV DB_PASSWORD pls_set_your_password
ENV DB_DATABASE wakeonlan

# 工作路径
WORKDIR /opt/wakeonlan

# 环境部署
COPY requirements requirements
RUN    python3 -m venv venv \
    && venv/bin/python3 -m pip install --upgrade pip \
    && . venv/bin/activate \
    && venv/bin/pip3 install -r requirements/docker.txt

# 拷贝源文件
COPY app app
COPY migrations migrations
COPY run.py entrypoint.sh ./

# 端口暴露
EXPOSE 5000

# 程序入口
ENTRYPOINT ["./entrypoint.sh"]
