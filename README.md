# wol
Wake on LAN

docker build -t custom-wol .
docker run -d -p 5000:5000 --name custom-wol custom-wol


http://ip:port/wake/00:11:22:33:44:55?host=255.255.255.255&port=9

1. 接口wol唤醒主机
2. ping 主机探活
3. ssh 关闭主机
4. 定时开关机（就是个定时任务）
根据 mac 换取内网ip地址
