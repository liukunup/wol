# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import paramiko
from wakeonlan import send_magic_packet
from multiping import MultiPing

class DeviceManager:

    def __init__(self, device):
        self.device = device

    def wakeup(self):
        """
        唤醒设备

        :return: 唤醒成功返回 True, 失败返回 False
        """
        try:
            # 发送魔法包以唤醒设备
            send_magic_packet(self.device['wol_mac'], ip_address=self.device['wol_host'], port=self.device['wol_port'])
            logger.info(f"设备 {self.device['name']} 已唤醒, 请稍等...")
            return True
        except Exception as e:
            logger.error(f"唤醒设备失败: {e}")
            return False

    def shutdown(self):
        """
        关闭设备

        :return: 关闭成功返回 True, 失败返回 False
        """
        command = "shutdown -h now"
        result = self.ssh(command)
        logger.info(f"设备 {self.device['name']} 已关机, 请稍等...")
        return result is not None

    def reboot(self):
        """
        重启设备

        :return: 重启成功返回 True, 失败返回 False
        """
        command = "reboot"
        result = self.ssh(command)
        logger.info(f"设备 {self.device['name']} 已重启, 请稍等...")
        return result is not None

    def ping(self):
        """
        检查设备是否在线

        :return: 在线返回 响应信息, 离线返回 None
        """
        mp = MultiPing([self.device['ssh_host']])
        mp.send()
        responses, no_responses = mp.receive(timeout=1)
        return self.device['ssh_host'] in responses

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
            client = paramiko.SSHClient()
            # 设置自动添加未知主机密钥策略
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.device['ssh_host'], port=self.device['ssh_port'],
                           username=self.device['username'], password=self.device['password'],
                           pkey=self.device['private_key'], key_filename=self.device['key_filename'],
                           passphrase=self.device['passphrase'])
            stdin, stdout, stderr = client.exec_command(command)
            return stdout.read().decode('utf-8')
        except Exception as e:
            logger.error(f"SSH 命令执行失败: {e}")
            return None
        finally:
            client.close()
