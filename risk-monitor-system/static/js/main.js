/**
 * Agent智能风险监控管理系统 - 主脚本
 */

// 全局配置
const API_BASE = '/api';

// 工具函数
function showAlert(type, message, containerId = 'alert-container') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const icons = { success: '✅', danger: '❌', warning: '⚠️', info: 'ℹ️' };
    container.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${icons[type] || ''} ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;

    // 3秒后自动消失
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('zh-CN', {
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit'
        });
    } catch {
        return dateStr;
    }
}

// API 请求封装
async function apiGet(endpoint) {
    const resp = await fetch(`${API_BASE}${endpoint}`);
    return resp.json();
}

async function apiPost(endpoint, data = {}) {
    const resp = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return resp.json();
}

async function apiPut(endpoint, data = {}) {
    const resp = await fetch(`${API_BASE}${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return resp.json();
}

async function apiDelete(endpoint) {
    const resp = await fetch(`${API_BASE}${endpoint}`, { method: 'DELETE' });
    return resp.json();
}

// 风险等级映射
const RISK_LEVEL_MAP = {
    'critical': { label: '🔴 重大风险', color: 'danger', score: '≥15' },
    'high': { label: '🟠 高度关注', color: 'warning', score: '10-14' },
    'medium': { label: '🟡 一般风险', color: 'info', score: '5-9' },
    'low': { label: '🟢 低风险', color: 'success', score: '<5' }
};

// 趋势映射
const TREND_MAP = {
    'increasing': { icon: '↑', label: '上升', color: 'danger' },
    'stable': { icon: '→', label: '稳定', color: 'secondary' },
    'decreasing': { icon: '↓', label: '下降', color: 'success' }
};

// 应对策略映射
const RESPONSE_MAP = {
    'avoid': { icon: '🚫', label: '规避' },
    'reduce': { icon: '🛡️', label: '降低' },
    'transfer': { icon: '🔄', label: '转移' },
    'accept': { icon: '✅', label: '接受' }
};

// 页面加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化系统信息
    fetchSystemInfo();

    // 初始化所有 tooltip
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(t => new bootstrap.Tooltip(t));
});

function fetchSystemInfo() {
    fetch('/api/system/info')
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                const badge = document.getElementById('model-badge');
                if (badge && d.data.model) {
                    badge.textContent = d.data.model === 'rule-engine' ?
                        '规则引擎模式' : 'AI: ' + d.data.model;
                }
            }
        })
        .catch(() => {});
}
