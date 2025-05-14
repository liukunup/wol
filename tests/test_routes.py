import pytest
import os
from app import create_app
from app.extensions import db

@pytest.fixture(scope="session", autouse=True)
def client():
    # 注入环境变量
    os.environ['KEEPASS_PASSWORD'] = "pls_use_strong_password"
    # 创建测试应用
    app = create_app("testing")
    # 创建数据库表
    with app.app_context():
        db.create_all()
    # 创建测试客户端
    with app.test_client() as client:
        yield client

@pytest.mark.run(order=-2)
def test_page_not_found(client):
    response = client.get('/page_not_found')
    assert response.status_code == 404

@pytest.mark.run(order=-3)
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

@pytest.mark.run(order=-1)
def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'code': 0, 'data': None, 'message': 'success'}

@pytest.mark.run(order=4)
def test_get_device_list(client):
    response = client.get('/device/all')
    assert response.status_code == 200

@pytest.mark.run(order=1)
def test_add_device(client):
    test_device_obj = {
        "name": "test_device",
        "wol_mac": "00:11:22:33:44:55",
        "wol_host": "255.255.255.255",
        "wol_port": 9,
        "ssh_host": "192.168.1.2",
        "ssh_port": 22,
        "ssh_username": "test_user",
        "ssh_password": "<password>",
        "ssh_pkey": "-----BEGIN RSA PRIVATE KEY----- ... -----END RSA PRIVATE KEY-----",
        "ssh_key_filename": "~/.ssh/id_rsa",
        "ssh_passphrase": "<passphrase>",
    }
    response = client.post('/device', json=test_device_obj)
    assert response.status_code == 200

@pytest.mark.run(order=2)
def test_get_device_by_id(client):
    test_id = 1
    response = client.get(f'/device/{test_id}')
    assert response.status_code == 200

@pytest.mark.run(order=3)
def test_update_device_by_id(client):
    test_id = 1
    updated_device = {
        "name": "test_device_x",
        "wol_mac": "11:22:33:44:55:66",
        "wol_host": "255.255.255.255",
        "wol_port": 9,
        "ssh_host": "192.168.1.3",
        "ssh_port": 22,
        "ssh_username": "test_user_x",
        "ssh_password": "<password-x>",
        "ssh_pkey": "-----BEGIN RSA PRIVATE KEY----- ... -----END RSA PRIVATE KEY-----",
        "ssh_key_filename": "~/.ssh/id_rsa.bak",
        "ssh_passphrase": "<passphrase-x>",
    }
    response = client.put(f'/device/{test_id}', json=updated_device)
    assert response.status_code == 200

@pytest.mark.run(order=5)
def test_delete_device_by_id(client):
    test_id = 1
    response = client.delete(f'/device/{test_id}')
    assert response.status_code == 200

@pytest.mark.skip("This test requires a valid device ID and operation type.")
def test_operate_device_by_id(client):
    test_id = 1
    test_op = 'wol'
    response = client.post(f'/device/{test_id}?op={test_op}')
    assert response.status_code == 200
