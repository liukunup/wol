import paramiko
from wakeonlan import send_magic_packet
from multiping import MultiPing

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
