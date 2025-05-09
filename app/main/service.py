
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
