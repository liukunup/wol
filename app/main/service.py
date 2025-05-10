# -*- coding: utf-8 -*-

from app.extensions import db
from app.device_manager import DeviceManager
from app.models import Device as DeviceModel
from app.response import ApiResponse

class DeviceService:
    """
    设备服务类
    """

    def get_all_devices(self):
        """
        获取所有设备信息
        """
        devices = {device.id: device for device in db.query(DeviceModel).all()}
        return Response(0, "成功", {id: device.to_dict() for id, device in devices.items()}).to_dict(), 200

    def get_device_by_id(self, id):
        """
        根据设备ID获取设备信息
        """
        return db.query(DeviceModel).filter_by(id=id).first()

    def update_device_by_id(self, id, device):
        """
        根据设备ID更新设备信息
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
        """
        self.db.add(device)
        self.db.commit()
        return True

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
