# -*- coding: utf-8 -*-

import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.orm import mapped_column, Mapped
from app.extensions import db

class DeviceModel(db.Model):
    """
    设备表: 用于存储设备信息, 包括设备名称/MAC地址/IP地址/端口号等
    """

    # 表名
    __tablename__ = 'device'

    # 字段
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="设备ID")
    name: Mapped[str] = mapped_column(nullable=False, comment="设备名称")
    status: Mapped[int] = mapped_column(nullable=False, default=3, comment="设备状态: 1-在线, 2-离线, 3-未知")
    delay: Mapped[float] = mapped_column(nullable=True, default=1, comment="延迟时间(秒)")
    last_uptime: Mapped[datetime] = mapped_column(nullable=True, comment="最后上线时间")
    last_heartbeat: Mapped[datetime] = mapped_column(nullable=True, comment="最后心跳时间")
    wol_mac: Mapped[str] = mapped_column(nullable=False, comment="[WOL] MAC地址")
    wol_host: Mapped[str] = mapped_column(nullable=True, comment="[WOL] IP地址或域名")
    wol_port: Mapped[int] = mapped_column(nullable=True, comment="[WOL] 端口号")
    ssh_host: Mapped[str] = mapped_column(nullable=False, comment="[SSH] IP地址或域名")
    ssh_port: Mapped[int] = mapped_column(nullable=False, comment="[SSH] 端口号")
    ssh_username: Mapped[str] = mapped_column(nullable=False, comment="[SSH] 账户")
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now(timezone.utc), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), comment="更新时间")

    def to_dict(self, timezone="UTC"):
        """
        将设备对象转换为字典

        :param timezone: 时区,默认为UTC
        :return: 包含设备信息的字典
        """
        # 转换时间为指定时区
        tz = ZoneInfo(timezone)
        if self.last_uptime: self.last_uptime = self.last_uptime.astimezone(tz).isoformat()
        if self.last_heartbeat: self.last_heartbeat = self.last_heartbeat.astimezone(tz).isoformat()
        if self.created_at: self.created_at = self.created_at.astimezone(tz).isoformat()
        if self.updated_at: self.updated_at = self.updated_at.astimezone(tz).isoformat()

        # 拆分字段
        wol_fields = [col for col in self.__table__.columns if col.name.startswith('wol_')]
        ssh_fields = [col for col in self.__table__.columns if col.name.startswith('ssh_')]
        other_fields = [col for col in self.__table__.columns if col not in wol_fields and col not in ssh_fields]

        # 构建字典
        result = {c.name: getattr(self, c.name) for c in other_fields}
        result.update({'wol': {c.name.replace('wol_', ''): getattr(self, c.name) for c in wol_fields}})
        result.update({'ssh': {c.name.replace('ssh_', ''): getattr(self, c.name) for c in ssh_fields}})

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
