// 从服务器获取主机数据
function fetchHostsData() {
    fetch(`${API_BASE_URL}/api/hosts`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('hostsContainer');
            if (data.hosts.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fas fa-server fa-3x text-muted mb-3"></i>
                        <p class="text-muted">没有可用的主机数据</p>
                    </div>
                `;
            } else {
                // 在实际应用中，这里可以使用前端模板引擎或直接操作DOM
                // 由于我们使用Jinja2服务器端渲染，这部分主要用于动态更新
                container.innerHTML = data.hosts.map(host => `
                    <div class="col-md-4 col-sm-6 mb-4">
                        <!-- 卡片HTML结构 -->
                    </div>
                `).join('');
            }
        })
        .catch(error => showError(error));
}

// 执行主机操作
function performAction(hostId, action, hostName) {
    fetch(`${API_BASE_URL}/api/hosts/${hostId}/${action}`, { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(`操作成功: ${hostName} 已${getActionName(action)}`);
        fetchHostsData(); // 刷新数据
    })
    .catch(error => {
        alert(`操作失败: ${error.message}`);
    });
}

// 获取操作名称
function getActionName(action) {
    const actions = {
        'wake': '唤醒',
        'restart': '重启',
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
            <button class="btn btn-primary mt-3" onclick="fetchHostsData()">
                <i class="fas fa-sync-alt me-1"></i>重试
            </button>
        </div>
    `;
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 如果页面是服务器端渲染的，不需要立即获取数据
    // 但如果需要实时更新，可以调用 fetchHostsData()
    
    // 刷新按钮事件
    document.getElementById('refreshBtn')?.addEventListener('click', fetchHostsData);
});