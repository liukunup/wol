# -*- coding: utf-8 -*-

from app.extensions import db
from app.main.host import DeviceManager
from app.main.models import DeviceModel
from app.main.response import ApiResponse

class DeviceService:
    """
    设备服务类
    """

    def get_all_devices(self):
        """
        获取所有设备信息
        """
        devices = db.session.query(DeviceModel).all()
        return ApiResponse(0, "success", [device.to_dict() for device in devices]).to_dict(), 200

    def get_device_by_id(self, id):
        """
        根据设备ID获取设备信息
        """
        device = db.session.query(DeviceModel).filter_by(id=id).first()
        if device:
            return ApiResponse(0, "success", device.to_dict()).to_dict(), 200
        else:
            return ApiResponse(-1, "device not found").to_dict(), 404

    def update_device_by_id(self, id, device):
        """
        根据设备ID更新设备信息
        """
        dev = db.session.query(DeviceModel).filter_by(id=id).first()
        if dev:
            print(device)
            for key, value in device.items():
                if key == "id": continue
                if not value: continue
                setattr(dev, key, value)
            db.session.commit()
            return ApiResponse(0, "success").to_dict(), 200
        return ApiResponse(-1, "server error").to_dict(), 500

    def delete_device_by_id(self, id):
        """
        根据设备ID删除设备信息
        """
        dev = db.session.query(DeviceModel).filter_by(id=id).first()
        if dev:
            db.session.delete(dev)
            db.session.commit()
            return ApiResponse(0, "success").to_dict(), 200
        return ApiResponse(-1, "server error").to_dict(), 500

    def add_device(self, device):
        """
        添加新的设备信息
        """
        dev = DeviceModel(**device)
        try:
            db.session.add(dev)
            db.session.commit()
            return ApiResponse(0, "success").to_dict(), 200
        except Exception as e:
            print(f"添加设备时出错: {e}")
            db.session.rollback()
            return ApiResponse(0, f"Failed\n{e}").to_dict(), 200

    def operate_device_by_id(self, id, op):
        """
        根据设备ID执行操作
        """
        if op is not None: op = op.lower()

        device = db.session.query(DeviceModel).filter_by(id=id).first()
        if not device:
            return ApiResponse(-1, "device not found").to_dict(), 404

        dm = DeviceManager(device)
        if op == "wol": # 唤醒
            result = dm.wakeup()
        elif op == "shutdown": # 关机
            result = dm.shutdown()
        elif op == "reboot": # 重启
            result = dm.reboot()
        elif op == "ping": # ping
            result = dm.ping()
        else:
            return ApiResponse(-1, "invalid operation").to_dict(), 400
        return ApiResponse(0, "success", result).to_dict(), 200
