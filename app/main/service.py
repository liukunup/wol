# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
from app.extensions import db
from .host import DeviceManager
from .models import DeviceModel
from .response import ApiResponse
from .vault import DeviceEntry, Vault

class DeviceService:
    """
    设备服务类
    """

    def __init__(self):
        password = os.getenv('VAULT_PASSWORD') or '123456'
        self.vault = Vault('vault.kdbx', password)

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
            title = str(id)
            # 获取密钥信息
            obj = self.vault.get(title)
            if obj:
                dev.ssh_password = obj['password']
                dev.ssh_pkey = obj['private_key']
                dev.ssh_key_filename = obj['key_filename']
                dev.ssh_passphrase = obj['passphrase']
            for key, value in device.items():
                if key == "id": continue
                if not value: continue
                setattr(dev, key, value)
            try:
                # 创建密钥条目
                entry = DeviceEntry(
                    id=id,
                    name=dev['name'],
                    host=dev['ssh_host'],
                    port=dev['ssh_port'],
                    username=dev['ssh_username'],
                    password=dev['ssh_password'],
                    private_key=dev['ssh_pkey'],
                    key_filename=dev['ssh_key_filename'],
                    passphrase=dev['ssh_passphrase']
                )
                # 安全删除密钥信息
                dev['ssh_password'] = None
                dev['ssh_pkey'] = None
                dev['ssh_key_filename'] = None
                dev['ssh_passphrase'] = None
                # 更新数据库
                db.session.commit()
                # 更新密钥条目
                self.vault.update(title, entry)
                return ApiResponse(0, "success").to_dict(), 200
            except Exception as e:
                logger.error(f"更新设备时出错: {e}")
                db.session.rollback()
        return ApiResponse(-1, "server error").to_dict(), 500

    def delete_device_by_id(self, id):
        """
        根据设备ID删除设备信息
        """
        dev = db.session.query(DeviceModel).filter_by(id=id).first()
        if dev:
            # 删除密钥条目
            title = str(id)
            self.vault.delete(title)
            # 删除数据库记录
            db.session.delete(dev)
            db.session.commit()
            return ApiResponse(0, "success").to_dict(), 200
        return ApiResponse(-1, "server error").to_dict(), 500

    def add_device(self, device):
        """
        添加新的设备信息
        """
        try:
            # 创建密钥条目
            entry = DeviceEntry(
                id=-1,  # 由于还没插入到数据库中,因此没有ID
                name=device['name'],
                host=device['ssh_host'],
                port=device['ssh_port'],
                username=device['ssh_username'],
                password=device['ssh_password'],
                private_key=device['ssh_pkey'],
                key_filename=device['ssh_key_filename'],
                passphrase=device['ssh_passphrase']
            )
            # 安全删除密钥信息
            device['ssh_password'] = None
            device['ssh_pkey'] = None
            device['ssh_key_filename'] = None
            device['ssh_passphrase'] = None
            # 添加数据库
            dev = DeviceModel(**device)
            db.session.add(dev)
            db.session.commit()
            # 更新密钥条目ID
            entry.id = dev.id
            # 再添加到密钥库中
            self.vault.insert(entry)
            return ApiResponse(0, "success").to_dict(), 200
        except Exception as e:
            logger.error(f"添加设备时出错: {e}")
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
        
        # 获取密钥信息
        title = str(id)
        obj = self.vault.get(title)
        if obj:
            device.ssh_password = obj['password']
            device.ssh_pkey = obj['private_key']
            device.ssh_key_filename = obj['key_filename']
            device.ssh_passphrase = obj['passphrase']

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
