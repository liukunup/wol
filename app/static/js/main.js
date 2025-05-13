// 获取主机数据
function fetchHosts(keyword = null) {
    let url = '/device/all';
    if (keyword) {
        url += `?keyword=${encodeURIComponent(keyword)}`;
    }
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.code !== 0) {
                alert(`获取主机数据失败: ${data.message}`);
            } else {
                const container = document.getElementById('hostsContainer');
                hosts = data.data;
                if (hosts.length === 0) {
                    // 如果没有主机数据，显示 Toast 提示
                    const toastElement = document.getElementById('hostsToast');
                    const toast = new bootstrap.Toast(toastElement);
                    toast.show();
                } else {
                    // 在实际应用中，这里可以使用前端模板引擎或直接操作DOM
                    // 由于我们使用Jinja2服务器端渲染，这部分主要用于动态更新
                    container.innerHTML = hosts.map(host => `
<div class="col-md-4 col-sm-6 mb-4">
    <div class="card h-100">
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">${host.name}</h5>
            <div class="col-auto">
                <div class="row icon-row">
                    <div class="col-auto">
                        <i class="fas fa-edit clickable-icon" onclick="editHost(${host.id})"></i>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-trash-alt clickable-icon" onclick="deleteHost(${host.id}, '${host.name}')"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="card-body">
            <div class="d-flex justify-content-between mb-2">
                <span class="fw-bold">${host.ssh.host || 'Host为空'}</span>
                <span class="status-${host.status || 'unknown'}">
                    <i class="fas fa-circle me-1 status-icon-${(() => {
                        if (host.status === 1) {
                            return 'online';
                        } else if (host.status === 2) {
                            return 'offline';
                        } else {
                            return 'unknown';
                        }
                    })()}"></i>
                    ${(() => {
                        if (host.status === 1) {
                            return '在线';
                        } else if (host.status === 2) {
                            return '离线';
                        } else {
                            return '未知';
                        }
                    })()}
                </span>
            </div>
            <div class="d-flex justify-content-between mb-2">
                <span>延迟时间</span>
                <span class="delay-${(() => {
                    const delay = parseInt(host.delay * 1000, 10);
                    if (!isNaN(delay)) {
                        if (delay >= 0 && delay < 10) {
                            return 'green';
                        } else if (delay >= 10 && delay < 30) {
                            return 'yellow';
                        } else {
                            return 'red';
                        }
                    }
                    return 'default';
                })()}">
                    ${host.delay !== undefined && host.delay !== null ? (host.delay >= 1 ? '--' : `${(host.delay * 1000).toFixed(2)}ms`) : '--'}
                </span>
            </div>
            <div class="d-flex justify-content-between mb-2">
                <span>上线时间</span>
                <div>
                    ${host.status === 1 ? (host.last_uptime ? (() => {
                        const date = new Date(host.last_uptime);
                        // 获取浏览器时区
                        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                        return date.toLocaleString('zh-CN', { 
                            year: 'numeric', 
                            month: '2-digit', 
                            day: '2-digit', 
                            hour: '2-digit', 
                            minute: '2-digit', 
                            second: '2-digit',
                            timeZone: timeZone
                        });
                    })() : '--') : '--'}
                </div>
            </div>
            <div class="d-flex justify-content-between mb-2">
                <span>在线时长</span>
                <div>
                    ${host.status === 1 ? `
                    <div>
                    ${(() => {
                        const uptime = new Date(host.last_heartbeat) - new Date(host.last_uptime);
                        const hours = Math.floor(uptime / (1000 * 60 * 60));
                        const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
                        const seconds = Math.floor((uptime % (1000 * 60)) / 1000);
                        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                    })()}
                    </div>
                    ` : '--'}
                </div>
            </div>
        </div>
        <div class="card-footer bg-white border-0 pt-0">
            <div class="row g-2">
                <div class="col-4">
                    <button class="btn btn-sm btn-outline-success action-btn" 
                        ${host.status === 1 ? 'disabled' : ''}
                        onclick="performAction(${host.id}, 'wol', '${host.name}')">
                        <i class="fas fa-power-off me-1"></i>唤醒
                    </button>
                </div>
                <div class="col-4">
                    <button class="btn btn-sm btn-outline-warning action-btn" 
                        ${host.status !== 1 ? 'disabled' : ''}
                        onclick="performAction(${host.id}, 'reboot', '${host.name}')">
                        <i class="fas fa-redo me-1"></i>重启
                    </button>
                </div>
                <div class="col-4">
                    <button class="btn btn-sm btn-outline-danger action-btn" 
                        ${host.status !== 1 ? 'disabled' : ''}
                        onclick="performAction(${host.id}, 'shutdown', '${host.name}')">
                        <i class="fas fa-power-off me-1"></i>关机
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
                    `).join('');
                }
            }
        })
        .catch(error => showError(error));
}

// 新增主机
function addHost(name,
    wolMac, wolHost, wolPort,
    sshHost, sshPort, sshUsername, sshPassword, sshPrivateKey, sshKeyFilename, sshPassphrase) {
    fetch(`/device`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name,
            wol_mac: wolMac, wol_host: wolHost, wol_port: wolPort,
            ssh_host: sshHost, ssh_port: sshPort, ssh_username: sshUsername,
            ssh_password: sshPassword, ssh_pkey: sshPrivateKey, ssh_key_filename: sshKeyFilename, ssh_passphrase: sshPassphrase
        })
    })
    .then(response => response.json())
   .then(data => {

        if (data.code !== 0) {
            const toastElement = document.getElementById('hostsToast');
            const toastBody = toastElement.querySelector('.toast-body');
            const toast = new bootstrap.Toast(toastElement);

            toastBody.textContent = `添加主机失败: ${data.message}`;

            toast.show();
        } else {
            fetchHosts(); // 刷新数据
        }

    })
}

// 搜索主机
function searchHosts() {
    const keyword = document.getElementById('hostSearch').value.trim();
    fetchHosts(keyword);
}

// 编辑主机
function editHost(hostId) {
    // 根据 hostId 获取主机信息
    fetch(`/device/${hostId}`)
    .then(response => response.json())
    .then(data => {
        if (data.code !== 0) {
            alert(`获取主机信息失败: ${data.message}`);
        } else {
            const host = data.data;
            // 填充模态框表单数据
            document.getElementById('name').value = host.name;
            document.getElementById('wolMac').value = host.wol.mac;
            document.getElementById('wolHost').value = host.wol.host;
            document.getElementById('wolPort').value = host.wol.port;
            document.getElementById('sshHost').value = host.ssh.host;
            document.getElementById('sshPort').value = host.ssh.port;
            document.getElementById('sshUsername').value = host.ssh.username;

            // 修改模态框标题
            document.getElementById('addHostModalLabel').textContent = '编辑主机';

            // 为提交按钮添加编辑主机的逻辑
            const submitButton = document.getElementById('submitHostForm');
            submitButton.onclick = function(event) {
                event.preventDefault();
                const form = document.getElementById('hostForm');
                if (form.checkValidity()) {
                    const name = document.getElementById('name').value;
                    const wolMac = document.getElementById('wolMac').value;
                    const wolHost = document.getElementById('wolHost').value;
                    const wolPort = document.getElementById('wolPort').value;
                    const sshHost = document.getElementById('sshHost').value;
                    const sshPort = document.getElementById('sshPort').value;
                    const sshUsername = document.getElementById('sshUsername').value;
                    const sshPassword = document.getElementById('sshPassword').value;
                    const sshPrivateKey = document.getElementById('sshPrivateKey').value;
                    const sshKeyFilename = document.getElementById('sshKeyFilename').value;
                    const sshPassphrase = document.getElementById('sshPassphrase').value;

                    // 调用更新接口
                    fetch(`/device/${hostId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: name,
                            wol_mac: wolMac,
                            wol_host: wolHost,
                            wol_port: wolPort,
                            ssh_host: sshHost,
                            ssh_port: sshPort,
                            ssh_username: sshUsername,
                            ssh_password: sshPassword,
                            ssh_pkey: sshPrivateKey,
                            ssh_key_filename: sshKeyFilename,
                            ssh_passphrase: sshPassphrase
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.code !== 0) {
                            alert(`更新主机失败: ${data.message}`);
                        } else {
                            fetchHosts(); // 刷新数据
                            const modal = bootstrap.Modal.getInstance(document.getElementById('hostModal'));
                            modal.hide();
                            // 恢复模态框标题
                            document.getElementById('addHostModalLabel').textContent = '添加主机';
                            // 恢复提交按钮的原始点击事件
                            submitButton.onclick = validateHostForm;
                        }
                    });
                }
            };

            // 显示模态框
            const modal = new bootstrap.Modal(document.getElementById('hostModal'));
            modal.show();
        }
    });
}

// 删除主机
function deleteHost(hostId, hostName) {
    if (confirm(`确定要删除主机 ${hostName} 的卡片吗？`)) {
        fetch(`/device/${hostId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.code!== 0) {
                alert(`删除主机失败: ${data.message}`);
            } else {
                fetchHosts(); // 刷新数据
            }
        })
    }
}

// 执行主机操作
function performAction(hostId, action, hostName) {
    fetch(`/device/${hostId}?op=${action}`, { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.code !== 0) {
            alert(`操作失败: ${data.message}`);
        } else {
            alert(`操作成功: ${hostName} 已${getActionName(action)}`);
            fetchHosts(); // 刷新数据
        }
    })
    .catch(error => {
        alert(`操作失败: ${error.message}`);
    });
}

// 获取操作名称
function getActionName(action) {
    const actions = {
        'wakeup': '唤醒',
        'reboot': '重启',
        'shutdown': '关机'
    };
    return actions[action] || action;
}

// 显示错误信息
function showError(error) {
    const container = document.getElementById('hostsContainer');
    container.innerHTML = `
        <div class="col-12 text-center py-5">
            <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
            <p class="text-danger">加载数据失败: ${error.message}</p>
            <button class="btn btn-primary mt-3" onclick="fetchHosts()">
                <i class="fas fa-sync-alt me-1"></i>重试
            </button>
        </div>
    `;
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 当页面加载完成时，刷新一次数据
    fetchHosts();

    // 为搜索框添加事件监听
    document.getElementById('hostSearch').addEventListener('input', function() {
        // 清空时刷新一次数据
        if (this.value === '') {
            fetchHosts();
        }
    });
    document.getElementById('hostSearch').addEventListener('keypress', function(e) {
        // 按下 Enter 键时触发搜索
        if (e.key === 'Enter') {
            searchHosts();
        }
    });

    // 为刷新按钮添加事件监听
    document.getElementById('refreshBtn')?.addEventListener('click', fetchHosts);

    // 为新增按钮添加事件监听
    document.getElementById('addHostBtn')?.addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('hostModal'));
        modal.show();
    });
});


function validateHostForm(event) {
    const form = document.getElementById('hostForm');
    // 检查表单的有效性，如果表单无效
    if (form.checkValidity() === false) {
        // 阻止表单的默认提交行为
        event.preventDefault();
        // 阻止事件冒泡
        event.stopPropagation();
    }
    // 为表单添加 'was-validated' 类，用于显示表单验证的样式
    form.classList.add('was-validated');
    // 再次检查表单的有效性，如果表单有效
    if (form.checkValidity() === true) {
        const name = document.getElementById('name').value;

        const wolMac = document.getElementById('wolMac').value;
        const wolHost = document.getElementById('wolHost').value;
        const wolPort = document.getElementById('wolPort').value;

        const sshHost = document.getElementById('sshHost').value;
        const sshPort = document.getElementById('sshPort').value;
        const sshUsername = document.getElementById('sshUsername').value;
        const sshPassword = document.getElementById('sshPassword').value;
        const sshPrivateKey = document.getElementById('sshPrivateKey').value;
        const sshKeyFilename = document.getElementById('sshKeyFilename').value;
        const sshPassphrase = document.getElementById('sshPassphrase').value;

        addHost(name, wolMac, wolHost, wolPort, sshHost, sshPort, sshUsername, sshPassword, sshPrivateKey, sshKeyFilename, sshPassphrase);

        const modal = bootstrap.Modal.getInstance(document.getElementById('hostModal'));
        modal.hide();
    }
}