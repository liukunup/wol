from flask import Flask, request
from wakeonlan import send_magic_packet

app = Flask(__name__)
devices = {"PC1": "00:11:22:33:44:55"}

@app.route("/wake/<device>")
def wake(device):
    mac = devices.get(device)
    if mac:
        send_magic_packet(mac)
        return f"已唤醒 {device}"
    return "设备不存在"

@app.route("/device")
def device():
    mac = devices.get(device)
    if mac:
        send_magic_packet(mac)
        return f"已唤醒 {device}"
    return "设备不存在"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
