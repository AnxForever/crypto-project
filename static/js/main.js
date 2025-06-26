/**
 * 密码学工具平台 - 通用JavaScript功能
 * 提供跨页面使用的通用函数和工具
 */

// 全局配置
const CONFIG = {
    API_BASE_URL: '',
    TOAST_DURATION: 3000,
    COPY_SUCCESS_MESSAGE: '已复制到剪贴板'
};

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeCommonFeatures();
});

/**
 * 初始化通用功能
 */
function initializeCommonFeatures() {
    // 初始化导航菜单高亮
    highlightCurrentPage();
    
    // 初始化复制按钮
    initializeCopyButtons();
    
    // 初始化表单验证
    initializeFormValidation();
    
    // 初始化响应式功能
    initializeResponsive();
}

/**
 * 高亮当前页面导航
 */
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-item');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href.split('/').pop())) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型: success, error, warning, info
 * @param {number} duration - 显示时长(毫秒)
 */
function showAlert(message, type = 'info', duration = CONFIG.TOAST_DURATION) {
    // 移除已存在的提示
    const existingAlert = document.querySelector('.custom-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // 创建新的提示元素
    const alert = document.createElement('div');
    alert.className = `custom-alert alert-${type}`;
    
    // 设置图标
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    alert.innerHTML = `
        <div class="alert-content">
            <i class="${icons[type] || icons.info}"></i>
            <span class="alert-message">${message}</span>
            <button class="alert-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // 添加到页面
    document.body.appendChild(alert);
    
    // 自动隐藏
    if (duration > 0) {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, duration);
    }
    
    // 添加显示动画
    setTimeout(() => {
        alert.classList.add('show');
    }, 10);
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 */
async function copyToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            // 备用方法
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            textArea.remove();
        }
        showAlert(CONFIG.COPY_SUCCESS_MESSAGE, 'success', 2000);
    } catch (error) {
        console.error('复制失败:', error);
        showAlert('复制失败，请手动复制', 'error');
    }
}

/**
 * 初始化复制按钮
 */
function initializeCopyButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-btn') || e.target.closest('.copy-btn')) {
            e.preventDefault();
            const button = e.target.classList.contains('copy-btn') ? e.target : e.target.closest('.copy-btn');
            const container = button.closest('.output-area, .key-content');
            if (container) {
                const text = container.textContent.replace('复制', '').trim();
                copyToClipboard(text);
            }
        }
    });
}

/**
 * 格式化字节大小
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 格式化时间
 * @param {number} milliseconds - 毫秒数
 */
function formatTime(milliseconds) {
    if (milliseconds < 1000) {
        return milliseconds.toFixed(2) + 'ms';
    } else if (milliseconds < 60000) {
        return (milliseconds / 1000).toFixed(2) + 's';
    } else {
        const minutes = Math.floor(milliseconds / 60000);
        const seconds = ((milliseconds % 60000) / 1000).toFixed(1);
        return minutes + 'm ' + seconds + 's';
    }
}

/**
 * 初始化表单验证
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // 移除错误样式
                    field.addEventListener('input', function() {
                        this.classList.remove('error');
                    }, { once: true });
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('请填写所有必填字段', 'warning');
            }
        });
    });
}

/**
 * 初始化响应式功能
 */
function initializeResponsive() {
    // 移动端菜单切换
    const mobileToggle = document.querySelector('.mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // 点击内容区域关闭菜单
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间
 * @param {boolean} immediate - 是否立即执行
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 时间限制
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * API请求封装
 * @param {string} url - 请求URL
 * @param {object} options - 请求选项
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(CONFIG.API_BASE_URL + url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

/**
 * 生成随机字符串
 * @param {number} length - 字符串长度
 * @param {string} charset - 字符集
 */
function generateRandomString(length = 16, charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') {
    let result = '';
    for (let i = 0; i < length; i++) {
        result += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    return result;
}

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * 验证身份证号格式
 * @param {string} idCard - 身份证号
 */
function validateIdCard(idCard) {
    const re = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;
    return re.test(idCard);
}

/**
 * 加载状态管理
 */
const LoadingManager = {
    show: function(element, text = '加载中...') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            element.disabled = true;
            element.dataset.originalText = element.innerHTML;
            element.innerHTML = `<span class="loading"></span> ${text}`;
        }
    },
    
    hide: function(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element && element.dataset.originalText) {
            element.disabled = false;
            element.innerHTML = element.dataset.originalText;
            delete element.dataset.originalText;
        }
    }
};

/**
 * 本地存储管理
 */
const StorageManager = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('存储失败:', error);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('读取存储失败:', error);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('删除存储失败:', error);
        }
    },
    
    clear: function() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('清空存储失败:', error);
        }
    }
};

// 导出到全局作用域（如果需要）
window.CryptoToolsApp = {
    showAlert,
    copyToClipboard,
    formatBytes,
    formatTime,
    debounce,
    throttle,
    apiRequest,
    generateRandomString,
    validateEmail,
    validateIdCard,
    LoadingManager,
    StorageManager
}; 