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
        password = os.getenv('VAULT_PASSWORD')
        self.vault = Vault('vault.kdbx', password)

    def get_all_devices(self, keyword=None):
        """
        获取所有设备信息
        """
        if keyword:
            devices = db.session.query(DeviceModel).filter(
                db.or_(
                    DeviceModel.name.like(f'%{keyword}%'),
                    DeviceModel.ssh_host.like(f'%{keyword}%')
                )
            ).all()
        else:
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
            # 更新数据库
            try:
                keys = ['ssh_password','ssh_pkey', 'ssh_key_filename', 'ssh_passphrase']
                for key, value in device.items():
                    if key == 'id': continue
                    if key in keys: continue
                    setattr(dev, key, value)
                db.session.commit()
            except Exception as e:
                logger.error(f"更新设备时出错: {e}")
                db.session.rollback()
                return ApiResponse(-1, "server error").to_dict(), 500

            # 更新密钥条目
            try:
                title = str(id)
                obj = self.vault.get(title)
                print(obj)
                if obj:
                    if 'ssh_password' in device:
                        obj['password'] = device['ssh_password']
                    if'ssh_pkey' in device:
                        obj['private_key'] = device['ssh_pkey']
                    if'ssh_key_filename' in device:
                        obj['key_filename'] = device['ssh_key_filename']
                    if'ssh_passphrase' in device:
                        obj['passphrase'] = device['ssh_passphrase']
                entry = DeviceEntry(
                    id=id,
                    name=dev.name,
                    host=dev.ssh_host,
                    port=dev.ssh_port,
                    username=dev.ssh_username,
                    password=obj['password'],
                    private_key=obj['private_key'],
                    key_filename=obj['key_filename'],
                    passphrase=obj['passphrase']
                )
                self.vault.update(title, entry)
            except Exception as e:
                logger.error(f"更新密钥时出错: {e}")
                return ApiResponse(-1, "server error").to_dict(), 500

            # 更新成功
            return ApiResponse(0, "success").to_dict(), 200
        else:
            return ApiResponse(-1, "device not found").to_dict(), 404

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
            # 显式安全删除密钥信息
            device.pop('ssh_password')
            device.pop('ssh_pkey')
            device.pop('ssh_key_filename')
            device.pop('ssh_passphrase')
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

        dev = db.session.query(DeviceModel).filter_by(id=id).first()
        if not dev:
            return ApiResponse(-1, "device not found").to_dict(), 404
        
        # 获取密钥信息
        title = str(id)
        obj = self.vault.get(title)

        # 合并设备信息和密钥信息
        device = {}
        device.update(dev.to_dict())
        device.pop('ssh_username')
        device.update(obj)

        # 执行操作
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
