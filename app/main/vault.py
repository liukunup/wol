# -*- coding: utf-8 -*-

import os
import json
from turtle import settiltangle
from pykeepass import PyKeePass, create_database


class DeviceEntry:

    def __init__(self, id: int, name: str,
                       host: str, port: int, username: str, password: str,
                       private_key: str, key_filename: str, passphrase: str):
        self.id = id
        self.name = name
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._private_key = private_key
        self._key_filename = key_filename
        self._passphrase = passphrase

    @property
    def title(self):
        return str(self.id)

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def notes(self):
        return f'Name: {self.name}\nHost: {self._host}\nPort: {self._port}'

    @property
    def binary(self):
        obj = {
            'private_key': self._private_key,
            'key_filename': self._key_filename,
            'passphrase': self._passphrase
        }
        content = json.dumps(obj, ensure_ascii=False)
        return content.encode('utf-8')

class Vault:

    _group_name = 'Hosts'

    def __init__(self, filename: str, password: str):
        if not password:
            raise Exception('Vault password is required')
        # 如果不存在,则创建一个新的数据库
        if not os.path.exists(filename):
            # 创建一个新的数据库文件
            self.__kp = create_database(filename, password=password)
            self._group = self.__kp.add_group(self.__kp.root_group, self._group_name)
        else:
            # 打开现有的数据库文件
            self.__kp = PyKeePass(filename, password=password)
            self._group = self.__kp.find_groups(self._group_name, first=True)

    def insert(self, dev: DeviceEntry):
        """
        添加一条记录
        """
        e = self.__kp.add_entry(self._group, dev.title, dev.username, dev.password, notes=dev.notes)
        binary_id = self.__kp.add_binary(dev.binary)
        e.add_attachment(binary_id, f'{dev.name}.bin')
        self.__kp.save()

    def update(self, title: str, dev: DeviceEntry):
        """
        更新一条记录
        """
        entry = self.__kp.find_entries(title=title, first=True)
        if entry:
            entry.username = dev.username
            entry.password = dev.password
            entry.notes = dev.notes
            binary_id = self.__kp.add_binary(dev.binary)
            entry.add_attachment(binary_id, f'{dev.name}.bin')
            self.__kp.save()

    def delete(self, title: str):
        """
        删除一条记录
        """
        entry = self.__kp.find_entries(title=title, first=True)
        if entry:
            self.__kp.delete_entry(entry)
            self.__kp.save()

    def get(self, title: str):
        """
        获取一条记录
        """
        entry = self.__kp.find_entries(title=title, first=True)
        if entry:
            attachments = self.__kp.find_attachments(filename=f'{dev.name}.bin', first=True)
            obj = json.loads(attachments[0].data.decode('utf-8'))
            return obj.update({'username': entry.username, 'password': entry.password})
        return None
