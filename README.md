# WOL

WOL(Wake on LAN) 是一个主机管理系统，同时兼具网络唤醒和远程控制功能。它允许用户通过网络唤醒远程计算机，并通过网络远程控制计算机的重启和关闭。

## 快速开始

- Windows

```powershell
docker run -d `
  -p 5000:5000 `
  -e KEEPASS_PASSWORD=pls_use_strong_password `
  -v wol-data:/wol/data `
  --name=wakeonlan `
  liukunup/wol:latest
```

- macOS/Linux

```shell
docker run -d \
  -p 5000:5000 \
  -e KEEPASS_PASSWORD=pls_use_strong_password \
  -v wol-data:/wol/data \
  --name=wakeonlan \
  liukunup/wol:latest
```

### 配置外置数据库

> 注意: 请事先创建好数据库，准备好数据库的用户名、密码。

```shell
docker run -d \
  -p 5000:5000 \
  -e KEEPASS_PASSWORD=pls_use_strong_password \
  -e DB_TYPE=mysql \
  -e DB_HOST=127.0.0.1 \
  -e DB_PORT=3306 \
  -e DB_USERNAME=wakeonlan \
  -e DB_PASSWORD=pls_use_strong_password \
  -e DB_SCHEMA=wakeonlan \
  -v wol-data:/wol/data \
  liukunup/wol:0.1.0
```

## 功能

- 网络唤醒
- 主机探活
- 远程控制（重启、关闭）

## 开发说明

### Windows

```powershell
# 设置密钥保管箱的密码(注意: 在生产环境中请使用强密码)
$env:KEEPASS_PASSWORD = "pls_use_strong_password"
# 创建数据表
flask db upgrade
# 启动服务
flask run
# 构建镜像
docker build -t liukunup/wol:0.1.0 -f Dockerfile .
```

### macOS/Linux

```bash
# 设置密钥保管箱的密码(注意: 在生产环境中请使用强密码)
export KEEPASS_PASSWORD="pls_use_strong_password"
# 创建数据表
flask db upgrade
# 启动服务
flask run
# 构建镜像
docker build -t liukunup/wol:0.1.0 -f Dockerfile .
```

## 许可证

MIT
