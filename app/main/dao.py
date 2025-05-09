

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
