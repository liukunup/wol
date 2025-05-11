# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timezone

from app.extensions import db, scheduler
from app.main.host import DeviceManager
from app.main.models import DeviceModel

# 配置日志
logging.basicConfig(level=logging.INFO)

@scheduler.task('interval', id='job_ping_all_devices', seconds=30)
def job_ping_all_devices():
    """
    定时任务: 定期ping所有设备
    """
    with scheduler.app.app_context():
        try:
            devices = db.session.query(DeviceModel).all()
            if not devices:
                return
            hosts = [device.ssh_host for device in devices]
            responses, no_responses = DeviceManager.ping_all(hosts)
            for host, delay_s in responses.items():
                device = db.session.query(DeviceModel).filter_by(ssh_host=host).first()
                if device:
                    # 设备状态变化
                    if device.status == 2 or device.status == 3:
                        device.last_uptime = datetime.now(timezone.utc)
                    device.status = 1
                    device.delay = delay_s
                    device.last_heartbeat = datetime.now(timezone.utc)
                    db.session.commit()
            for host in no_responses:
                device = db.session.query(DeviceModel).filter_by(ssh_host=host).first()
                if device:
                    device.status = 2
                    device.delay = None
                    db.session.commit()
        except Exception as e:
            logging.error(f"定时任务执行出错: {e}")
            db.session.rollback()
        finally:
            db.session.close()
