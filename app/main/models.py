from sqlalchemy.orm import mapped_column, Mapped
from extensions import db


class DeviceModel(db.Model):
    """
    设备表: 用于存储设备信息, 包括设备名称/MAC地址/IP地址/端口号等
    """

    # 表名
    __tablename__ = 'device'

    # 字段
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="设备ID")
    name: Mapped[str] = mapped_column(nullable=False, comment="自定义设备名称")
    wol_mac: Mapped[str] = mapped_column(nullable=True, comment="[WOL] MAC地址")
    wol_host: Mapped[str] = mapped_column(nullable=True, comment="[WOL] IP地址或域名")
    wol_port: Mapped[int] = mapped_column(nullable=True, comment="[WOL] 端口号")
    ssh_ip: Mapped[str] = mapped_column(nullable=True, comment="[SSH] IP地址或域名")
    ssh_port: Mapped[int] = mapped_column(nullable=True, comment="[SSH] 端口号")
    ssh_username: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 账户")
    ssh_password: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 密码")
    ssh_pkey: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 密钥字符串")
    ssh_key_filename: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 密钥文件名")
    ssh_passphrase: Mapped[str] = mapped_column(nullable=True, comment="[SSH] 密钥的密码")

    def to_dict(self, secure=True):
        """
        将设备对象转换为字典

        :param secure: 是否安全返回,如果为True,则不会返回密码和密钥等敏感信息
        :return: 包含设备信息的字典
        """
        # 拆分字段
        wol_fields = [col for col in self.__table__.columns if col.name.startswith('wol_')]
        ssh_fields = [col for col in self.__table__.columns if col.name.startswith('ssh_')]
        other_fields = [col for col in self.__table__.columns if col not in wol_fields and col not in ssh_fields]
        # 构建字典
        result = {c.name: getattr(self, c.name) for c in other_fields}
        result.update({'wol': {c.name.replace('wol_', ''): getattr(self, c.name) for c in wol_fields}})
        result.update({'ssh': {c.name.replace('ssh_', ''): getattr(self, c.name) for c in ssh_fields}})
        # 移除密钥
        if secure and 'ssh' in result:
            if 'password' in result['ssh']:
                result['ssh']['password'] = None
            if 'pkey' in result['ssh']:
                result['ssh']['pkey'] = None
            if 'key_filename' in result['ssh']:
                result['ssh']['key_filename'] = None
            if 'passphrase' in result['ssh']:
                result['ssh']['passphrase'] = None
        return result

    def __str__(self):
        """
        将设备对象转换为JSON字符串

        :return: 包含设备信息的JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self):
        """
        返回设备对象的字符串表示

        :return: 设备对象的字符串表示
        """
        return f'<Device {self.name}>'
