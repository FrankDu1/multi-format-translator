/**
 * Environment Configuration Loader
 * Loads configuration from .env, meta tags, or localStorage
 * 
 * Usage:
 *   await ENV_CONFIG.load();
 *   const apiUrl = ENV_CONFIG.getApiUrl();
 *   ENV_CONFIG.debug();
 */

// 环境配置管理
const ENV_CONFIG = (() => {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    console.log('🔍 环境检测:', { hostname, pathname });
    
    // 检测是否在 /trans 路径下
    const isUnderTransPath = pathname.startsWith('/trans');
    
    // 本地开发环境
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        console.log('✅ 检测到本地环境');
        return {
            API_BASE_URL: 'http://localhost:5002/api',
            isProduction: false
        };
    }
    
    // IP 地址访问（Docker 直连测试）
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (ipPattern.test(hostname)) {
        const port = window.location.port || '5001';
        const apiPort = '5002';
        console.log('✅ 检测到 IP 地址访问');
        return {
            API_BASE_URL: `http://${hostname}:${apiPort}/api`,
            isProduction: false
        };
    }
    
    // 域名访问（生产环境）- 使用 nginx 代理
    console.log('✅ 检测到域名访问（生产环境）');
    
    // 如果在 /trans 路径下，API 使用相对路径 /translator-api/api
    if (isUnderTransPath) {
        console.log('📍 检测到 /trans 路径，使用 nginx 代理路径');
        return {
            API_BASE_URL: '/translator-api/api',
            BASE_PATH: '/trans',  // 新增：基础路径
            isProduction: true
        };
    }
    
    // 默认配置（根路径）
    return {
        API_BASE_URL: '/translator-api/api',
        BASE_PATH: '',
        isProduction: true
    };
})();

// 加载 .env 文件（仅本地开发）
async function loadEnvFile() {
    // 只在本地环境加载 .env 文件
    if (ENV_CONFIG.isProduction) {
        console.log('⏭️  生产环境，跳过 .env 文件加载');
        return;
    }
    
    try {
        const response = await fetch('/.env');
        if (!response.ok) {
            console.log('ℹ️  未找到 .env 文件，使用默认配置');
            return;
        }
        
        const text = await response.text();
        const lines = text.split('\n');
        
        lines.forEach(line => {
            line = line.trim();
            if (line && !line.startsWith('#')) {
                const [key, ...valueParts] = line.split('=');
                const value = valueParts.join('=').trim();
                if (key && value) {
                    window.ENV = window.ENV || {};
                    window.ENV[key.trim()] = value.replace(/^["']|["']$/g, '');
                }
            }
        });
        
        console.log('✅ .env 文件加载成功');
    } catch (error) {
        console.log('ℹ️  .env 文件加载失败:', error.message);
    }
}

// 页面加载时自动加载环境变量
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadEnvFile);
} else {
    loadEnvFile();
}

console.log('📋 当前环境配置:', ENV_CONFIG);
