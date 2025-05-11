# -*- coding: utf-8 -*-

import paramiko
from wakeonlan import send_magic_packet
from multiping import MultiPing
from app.main.models import DeviceModel

class DeviceManager:

    def __init__(self, device: DeviceModel):
        self.device = device

    def wakeup(self):
        """
        唤醒设备

        :return: 唤醒成功返回 True, 失败返回 False
        """
        try:
            # 发送魔法包以唤醒设备
            send_magic_packet(self.device.wol_mac, ip_address=self.device.wol_host, port=self.device.wol_port)
            return True
        except Exception as e:
            print(f"唤醒设备失败: {e}")
            return False

    def shutdown(self):
        """
        关闭设备

        :return: 关闭成功返回 True, 失败返回 False
        """
        command = "shutdown -h now"
        result = self.ssh(command)
        return result is not None

    def reboot(self):
        """
        重启设备

        :return: 重启成功返回 True, 失败返回 False
        """
        command = "reboot"
        result = self.ssh(command)
        return result is not None

    def ping(self):
        """
        检查设备是否在线

        :return: 在线返回 响应信息, 离线返回 None
        """
        mp = MultiPing([self.device.ssh_host])
        mp.send()
        responses, no_responses = mp.receive(timeout=1)
        return self.device.ssh_host in responses

    @staticmethod
    def ping_all(hosts):
        """
        检查多个设备是否在线

        :param hosts: 设备列表
        :return: 在线设备列表, 离线设备列表
        """
        mp = MultiPing(hosts)
        mp.send()
        return mp.receive(timeout=1)

    def ssh(self, command):
        """
        执行 SSH 命令

        :param command: SSH 命令
        :return: 命令执行结果, 如果执行失败则返回 None
        """
        try:
            # 创建 SSH 客户端对象
            client = paramiko.SSHClient()
            # 设置自动添加未知主机密钥策略
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接到设备
            client.connect(self.device.ssh_ip, port=self.device.ssh_port,
                           username=self.device.ssh_username, password=self.device.ssh_password,
                           pkey=self.device.ssh_pkey, key_filename=self.device.ssh_key_filename,
                           passphrase=self.device.ssh_passphrase)
            # 执行 SSH 命令
            stdin, stdout, stderr = client.exec_command(command)
            # 返回命令执行结果
            return stdout.read().decode('utf-8')
        except Exception as e:
            print(f"执行SSH命令失败: {e}")
            return None
        finally:
            # 关闭 SSH 连接
            client.close()
