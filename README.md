# WOL

WOL(Wake on LAN) 是一个主机管理系统，同时兼具网络唤醒和远程控制功能。它允许用户通过网络唤醒远程计算机，并通过网络远程控制计算机的重启和关闭。

## 功能

- 网络唤醒
- 主机探活
- 远程控制（重启、关闭）

## 快速开始

## 开发说明

### Windows

```powershell
# 设置密钥保管箱的密码(注意: 在生产环境中请使用强密码)
$env:VAULT_PASSWORD = "123456"
# 启动服务
flask run
```

### MacOS/Linux

```bash
# 设置密钥保管箱的密码(注意: 在生产环境中请使用强密码)
export VAULT_PASSWORD="123456"
# 启动服务
flask run
```

## 许可证

MIT
