import pytest
from app.main.routes import blueprint
from flask import Flask

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

def test_not_found(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_system_health_check(client):
    response = client.get('/system/health')
    assert response.status_code == 200
    assert response.json == {'code': 0, 'message': 'success'}

def test_get_device_list(client):
    response = client.get('/device/all')
    assert response.status_code == 200

def test_add_device(client):
    test_device = {
        # 根据实际情况填写设备信息
    }
    response = client.post('/device', json=test_device)
    assert response.status_code in [200, 400]  # 具体状态码根据业务逻辑调整

def test_get_device_by_id(client):
    test_id = 1  # 根据实际情况填写设备 ID
    response = client.get(f'/device/{test_id}')
    assert response.status_code in [200, 404]  # 具体状态码根据业务逻辑调整

def test_update_device_by_id(client):
    test_id = 1  # 根据实际情况填写设备 ID
    updated_device = {
        # 根据实际情况填写更新的设备信息
    }
    response = client.put(f'/device/{test_id}', json=updated_device)
    assert response.status_code in [200, 404]  # 具体状态码根据业务逻辑调整

def test_delete_device_by_id(client):
    test_id = 1  # 根据实际情况填写设备 ID
    response = client.delete(f'/device/{test_id}')
    assert response.status_code in [200, 404]  # 具体状态码根据业务逻辑调整

def test_operate_device_by_id(client):
    test_id = 1  # 根据实际情况填写设备 ID
    test_op = 'wol'  # 根据实际情况填写操作类型
    response = client.post(f'/device/{test_id}?op={test_op}')
    assert response.status_code in [200, 400, 404]  # 具体状态码根据业务逻辑调整