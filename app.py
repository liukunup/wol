import os
import json
import paramiko

from flask import Flask, request, render_template
from wakeonlan import send_magic_packet
from multiping import MultiPing
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


class DeviceModel(db.Model):
    """
    设备表: 用于存储设备信息,包括设备名称/MAC地址/IP地址/端口号等
    """

    # 表名
    __tablename__ = 'device'

    # 字段
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="设备ID")
    name: Mapped[str] = mapped_column(nullable=False, comment="自定义设备名称")
    wol_mac: Mapped[str] = mapped_column(nullable=True, comment="[WOL] MAC地址")
    wol_host: Mapped[str] = mapped_column(nullable=True, comment="[WOL] IP地址或域名")
    wol_port: Mapped[int] = mapped_column(nullable=True, comment="[WOL] 端口号")
    ssh_ip: Mapped[str] = mapped_column(nullable=True, comment="[SSH] IP地址或域名")
    ssh_port: Mapped[int] = mapped_column(nullable=True, comment="[SSH] 端口号")
    ssh_username: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 账户")
    ssh_password: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 密码")
    ssh_pkey: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 密钥字符串")
    ssh_key_filename: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 密钥文件名")
    ssh_passphrase: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 密钥的密码")

    def to_dict(self, secure=True):
        """
        将设备对象转换为字典

        :param secure: 是否安全返回,如果为True,则不会返回密码和密钥等敏感信息
        :return: 包含设备信息的字典
        """
        # 拆分字段
        wol_fields = [col for col in self.__table__.columns if col.name.startswith('wol_')]
        ssh_fields = [col for col in self.__table__.columns if col.name.startswith('ssh_')]
        other_fields = [col for col in self.__table__.columns if col not in wol_fields and col not in ssh_fields]
        # 构建字典
        result = {c.name: getattr(self, c.name) for c in other_fields}
        result.update({'wol': {c.name.replace('wol_', ''): getattr(self, c.name) for c in wol_fields}})
        result.update({'ssh': {c.name.replace('ssh_', ''): getattr(self, c.name) for c in ssh_fields}})
        # 移除密钥
        if secure and 'ssh' in result:
            if 'password' in result['ssh']:
                result['ssh']['password'] = None
            if 'pkey' in result['ssh']:
                result['ssh']['pkey'] = None
            if 'key_filename' in result['ssh']:
                result['ssh']['key_filename'] = None
            if 'passphrase' in result['ssh']:
                result['ssh']['passphrase'] = None
        return result

    def __str__(self):
        """
        将设备对象转换为JSON字符串

        :return: 包含设备信息的JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self):
        """
        返回设备对象的字符串表示

        :return: 设备对象的字符串表示
        """
        return f'<Device {self.name}>'


class DeviceDAO:
    """
    设备数据访问对象类,定义设备信息的增删改查接口
    """

    def __init__(self, dbo):
        """
        初始化设备数据访问对象

        :param dbo: 数据库对象
        """
        self.db = dbo

    def get_all_devices(self):
        """
        获取所有设备信息

        :return: 包含所有设备信息的字典
        """
        return {device.id: device for device in self.db.query(DeviceModel).all()}

    def get_device_by_id(self, id):
        """
        根据设备ID获取设备信息

        :param id: 设备ID
        :return: 对应的设备信息,如果不存在则返回None
        """
        return self.db.query(DeviceModel).filter_by(id=id).first()

    def update_device_by_id(self, id, device):
        """
        根据设备ID更新设备信息

        :param id: 设备ID
        :param device: 新的设备信息
        :return: 更新成功返回True,失败返回False
        """
        dev = self.get_device_by_id(id)
        if dev:
            for key, value in device.items():
                setattr(dev, key, value)
            self.db.commit()
            return True
        return False

    def delete_device_by_id(self, id):
        """
        根据设备ID删除设备信息

        :param id: 设备ID
        :return: 删除成功返回True,失败返回False
        """
        dev = self.get_device_by_id(id)
        if dev:
            self.db.delete(dev)
            self.db.commit()
            return True
        return False

    def add_device(self, device):
        """
        添加新的设备信息

        :param device: 新的设备信息
        :return: 添加成功返回True,失败返回False
        """
        self.db.add(device)
        self.db.commit()
        return True


class DeviceManager:
    """
    设备操作服务类,提供设备相关的操作
    """

    def __init__(self, device):
        """
        初始化设备操作服务

        :param device: 设备信息
        """
        self.device = device

    def wakeup(self):
        """
        唤醒设备

        :return: 唤醒成功返回True,失败返回False
        """
        try:
            send_magic_packet(self.device.wol_mac, ip_address=self.device.wol_host, port=self.device.wol_port)
            return True
        except Exception as e:
            print(f"唤醒设备失败: {e}")
            return False

    def shutdown(self):
        """
        关闭设备

        :return: 关闭成功返回True,失败返回False
        """
        command = "shutdown -h now"
        result = self.ssh(command)
        return result is not None

    def reboot(self):
        """
        重启设备

        :return: 重启成功返回True,失败返回False
        """
        command = "reboot"
        result = self.ssh(command)
        return result is not None

    def ping(self):
        """
        检查设备是否在线

        :return: 在线返回True,离线返回False
        """
        mp = MultiPing([self.device.wol_host], timeout=1, retry=1)
        mp.send()
        responses, no_responses = mp.receive()
        return self.device.wol_host in responses

    def ssh(self, command):
        """
        执行SSH命令

        :param command: SSH命令
        :return: 命令执行结果
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.device.ssh_ip, port=self.device.ssh_port,
                           username=self.device.ssh_username, password=self.device.ssh_password,
                           pkey=self.device.ssh_pkey, key_filename=self.device.ssh_key_filename,
                           passphrase=self.device.ssh_passphrase)
            stdin, stdout, stderr = client.exec_command(command)
            return stdout.read().decode('utf-8')
        except Exception as e:
            print(f"执行SSH命令失败: {e}")
            return None
        finally:
            client.close()


class DeviceService:
    """
    设备服务类：提供设备相关的业务逻辑操作
    """

    def __init__(self):
        self.__database_type = os.environ.get('DB_TYPE', 'sqlite') # [sqlite, mysql, mariadb, postgresql]
        self.__database_type = self.__database_type.lower()
        if self.__database_type in ['mysql', 'mariadb', 'postgresql']:
            self.__database_host = os.environ.get('DB_HOST', 'localhost')
            self.__database_port = os.environ.get('DB_PORT', '3306')
            self.__database_username = os.environ.get('DB_USERNAME', 'wakeonlan')
            self.__database_password = os.environ.get('DB_PASSWORD', 'pls_set_stronger_password')
            self.__database_name = os.environ.get('DB_NAME', 'wakeonlan')
            self.database_url = f'{self.__database_type}://{self.__database_username}:{self.__database_password}@{self.__database_host}:{self.__database_port}/{self.__database_name}'
        else:
            self.__database_name = os.environ.get('DB_NAME', 'wakeonlan')
            self.database_url = f'sqlite:///{self.__database_name}.db'
        self.db = None

    def init_database(self, _app, _dbo):
        """
        初始化数据库

        :param _app: Flask应用对象
        :param _dbo: 数据库对象
        """
        _app.config["SQLALCHEMY_DATABASE_URI"] = self.database_url
        _dbo.init_app(_app)
        with _app.app_context():
            try:
                _dbo.create_all()
                print("Database tables created successfully.")
            except Exception as e:
                print(f"Failed to create database tables: {e}")
        self.db = _dbo

    def get_all_devices(self):
        """
        获取所有设备信息
        """
        devices = DeviceDAO(self.db).get_all_devices()
        return Response(0, "成功", {id: device.to_dict() for id, device in devices.items()}).to_dict(), 200
    
    def get_device_by_id(self, id):
        """
        根据设备ID获取设备信息
        """
        return DeviceDAO(self.db).get_device_by_id(id)

    def update_device_by_id(self, id, device):
        """
        根据设备ID更新设备信息
        """
        return DeviceDAO(self.db).update_device_by_id(id, device)

    def delete_device_by_id(self, id):
        """
        根据设备ID删除设备信息
        """
        return DeviceDAO(self.db).delete_device_by_id(id)

    def add_device(self, device):
        """
        添加新的设备信息
        """
        return DeviceDAO(self.db).add_device(device)

    def operate_device_by_id(self, id, op):
        """
        根据设备ID执行操作
        """
        if op: op = op.lower()

        device = self.get_device_by_id(id)
        if not device:
            return "设备不存在", 404

        dm = DeviceManager(device)
        if op == "wakeup": # 唤醒
            result = dm.wakeup()
        elif op == "shutdown": # 关机
            result = dm.shutdown()
        elif op == "reboot": # 重启
            result = dm.reboot()
        elif op == "ping": # ping
            result = dm.ping()
        else:
            return "无效的操作", 400
        return result


class Response:
    """
    响应对象类,用于封装API接口的响应信息
    """

    def __init__(self, code, message, data=None):
        """
        初始化响应对象

        :param code: 响应状态码
        :param msg: 响应消息
        :param data: 响应数据,默认为None
        """
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        """
        将响应对象转换为字典

        :return: 包含响应信息的字典
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


@app.route("/system/health", methods=["GET"])
def system_health_check():
    return Response(0, "成功").to_dict(), 200

@app.route("/system/initdb", methods=["POST"])
def system_init_database():
    return Response(0, "成功").to_dict(), 200

@app.route("/device/all", methods=["GET"])
def get_device_list():
    return service.get_all_devices()

@app.route("/device/<id>", methods=["GET"])
def get_device_by_id(id):
    return service.get_device_by_id(id)

@app.route("/device/<id>", methods=["PUT"])
def update_device_by_id(id):
    return service.update_device_by_id(id, request.json)

@app.route("/device/<id>", methods=["DELETE"])
def delete_device_by_id(id):
    return service.delete_device_by_id(id)

@app.route("/device/<id>", methods=["POST"])
def operate_device_by_id(id):
    op = request.args.get("op", default=None, type=str)
    return service.operate_device_by_id(id, op)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


service = DeviceService()


if __name__ == "__main__":
    service.init_database(app, db)
    app.run(host='0.0.0.0', port=5000)
