import os
import json
import paramiko

from flask import Flask, request
from wakeonlan import send_magic_packet
from multiping import MultiPing

app = Flask(__name__)

# 环境变量
e_database_type = os.environ.get('DB_TYPE', 'json') # [json, sqlite, mysql, mariadb]
e_database_host = os.environ.get('DB_HOST', 'localhost')
e_database_port = os.environ.get('DB_PORT', '3306')
e_database_username = os.environ.get('DB_USERNAME', 'wakeonlan')
e_database_password = os.environ.get('DB_PASSWORD', 'pls_set_stronger_password')
e_database_name = os.environ.get('DB_NAME', 'wakeonlan')

# 全局变量
g_devices = {}

# 样例数据
sample_devices = {
    "1": {
        "name": "样例数据",
        "mac": "11:22:33:44:55:66",
        "host": "255.255.255.255",
        "port": 9,
        "ssh": {
            "ip": "192.168.0.8",
            "port": 22,
            "username": "root",
            "password": "",
            "pkey": "私钥内容",
            "key_filename": "私钥文件",
            "passphrase": "私钥密码"
        }
    }
}


def load_config_from_json():
    # 读取配置文件
    if not os.access('device.json', os.R_OK):
        # 如果配置文件不存在，则创建一个空的配置文件
        with open('device.json', 'w') as f:
            f.write(json.dumps(sample_devices, indent=4, ensure_ascii=False))
        return {}
    else:
        with open('device.json', 'r') as f:
            try:
                conf = json.load(f)
                return conf
            except json.JSONDecodeError:
                # 如果配置文件格式不正确，则返回空字典
                return {}

def save_config_to_json(devices):
    # 保存或更新到配置文件
    with open('device.json', 'w') as f:
        try:
            json.dump(devices, f, indent=4, ensure_ascii=False)
        except TypeError:
            return False
    return True

def load_config_from_database():
    # 从数据库读取配置
    return {}

def save_config_to_database(devices):
    # 保存或更新到数据库
    return True


@app.route("/devices", methods=["GET"])
def get_device_list():
    return g_devices, 200

@app.route("/device/<id>", methods=["GET"])
def get_device_by_id(id):
    return g_devices.get(id, "设备不存在"), 404

@app.route("/device/<id>", methods=["PUT"])
def update_device_by_id(id):
    # 选取字段
    fields = ["name", "mac", "ip", "port", "ssh"]
    # 检查请求体
    if not request.json:
        return "请求体不能为空", 400
    # 检查请求体字段
    for field in fields:
        if field not in request.json:
            return f"缺少字段: {field}", 400
    g_devices.update({id: request.json})
    return "设备已更新", 200

@app.route("/device/<id>", methods=["DELETE"])
def delete_device_by_id(id):
    device = g_devices.get(id)
    if not device:
        return "设备不存在", 404
    # 删除设备
    g_devices.pop(id)
    save_config_to_json(g_devices)
    return "设备已删除", 200

def wakeup(id: int):
    """
    唤醒设备
    :param id: ID
    :return: msg, code
    """
    # 获取待唤醒的设备
    device = g_devices.get(id)
    if not device:
        return "设备不存在", 404

    mac = device.get("mac")
    if not mac:
        return "设备不存在", 404
    ip = device.get("ip")
    if not ip:
        return "设备不存在", 404
    port = device.get("port")
    if not port:
        return "设备不存在", 404
    name = device.get("name")
    if not name:
        name = "未命名设备", 404

    # 唤醒设备
    try:
        # 发送唤醒包
        send_magic_packet(mac, ip_address=ip, port=port)
        return f"已唤醒 {name}", 200
    except Exception as e:
        return f"唤醒失败: {str(e)}", 500

def shutdown(id: int):
    """
    关机设备
    :param id: ID
    :return: msg, code
    """
    # 获取待关机的设备
    device = g_devices.get(id)
    if not device:
        return "设备不存在", 404

    ip = device.get("ssh").get("ip")
    port = device.get("ssh").get("port")
    username = device.get("ssh").get("username")
    password = device.get("ssh").get("password")
    pkey = device.get("ssh").get("pkey")
    key_filename = device.get("ssh").get("key_filename")
    passphrase = device.get("ssh").get("passphrase")

    name = device.get("name")
    if not name:
        name = "未命名设备"

    # 关机设备
    try:
        # 创建SSH对象
        ssh_client = paramiko.SSHClient()

        # 允许连接不在know_hosts文件中的主机
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接服务器
        ssh_client.connect(hostname=ip, port=port, username=username, password=password,
                           pkey=pkey, key_filename=key_filename, passphrase=passphrase)

        # 执行命令
        stdin, stdout, stderr = ssh_client.exec_command("shutdown -h now")

        # 获取命令结果
        result = stdout.read().decode()
        error = stderr.read().decode()

        # 关闭连接
        ssh_client.close()

        return f"已关机 {name}", 200
    except Exception as e:
        return f"关机失败: {str(e)}", 500

def ping(id: int):
    """
    ping设备
    :param id: ID
    :return: msg, code
    """
    # 获取待ping的设备
    device = g_devices.get(id)
    if not device:
        return "设备不存在", 404

    ip = device.get("ip")
    if not ip:
        return "设备不存在", 404
    name = device.get("name")
    if not name:
        name = "未命名设备", 404

    # ping设备
    try:
        # 创建MultiPing对象
        mp = MultiPing([ip])

        # 发送ping请求
        mp.send()

        # 获取响应结果
        response = mp.receive(timeout=1)

        # 关闭连接
        mp.close()

        # 检查响应结果
        if response[ip] == 0:
            return f"{name} 在线", 200
        else:
            return f"{name} 离线", 500

    except Exception as e:
        return f"ping失败: {str(e)}", 500

@app.route("/device/<id>", methods=["POST"])
def operate_device_by_id(id):
    op = request.args.get("op", default=None, type=str)

    if not id:
        return "缺少设备ID", 400

    if op:
        op = op.lower()

    if op == "wakeup": # 唤醒
        result = wakeup(id)
    elif op == "shutdown": # 关机
        result = shutdown(id)
    elif op == "ping": # ping
        result = ping(id)
    else:
        return "无效的操作", 400
    return result


if __name__ == "__main__":
    # 加载配置
    if e_database_type.lower() in ['mysql', 'mariadb']:
        g_devices = load_config_from_database()
    else:
        g_devices = load_config_from_json()
    # 启动应用
    app.run(host='0.0.0.0', port=5000)
