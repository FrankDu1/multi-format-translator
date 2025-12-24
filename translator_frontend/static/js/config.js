// API 配置文件
// 支持多环境配置

const CONFIG = {
    // 开发环境配置
    development: {
        API_BASE_URL: 'http://localhost:5002',
        API_ENDPOINTS: {
            UPLOAD: '/upload',
            TRANSLATE_TEXT: '/translate-text',
            TRANSLATE_PDF: '/upload',
            TRANSLATE_IMAGE: '/api/translate/image',
            TRANSLATE_PPT: '/translate-ppt',
            STATUS: '/status'
        }
    },
    
    // Docker Compose 环境配置
    docker: {
        API_BASE_URL: 'http://localhost:5002',  // 使用 Docker 内部网络
        API_ENDPOINTS: {
            UPLOAD: '/upload',
            TRANSLATE_TEXT: '/translate-text',
            TRANSLATE_PDF: '/upload',
            TRANSLATE_IMAGE: '/api/translate/image',
            TRANSLATE_PPT: '/translate-ppt',
            STATUS: '/status'
        }
    },
    
    // 生产环境配置
    production: {
        API_BASE_URL: 'http://localhost:5002',  // 使用相对路径，通过 Nginx 反向代理
        API_ENDPOINTS: {
            UPLOAD: '/api/upload',
            TRANSLATE_TEXT: '/api/translate-text',
            TRANSLATE_PDF: '/api/upload',
            TRANSLATE_IMAGE: '/api/translate/image',
            TRANSLATE_PPT: '/api/translate-ppt',
            STATUS: '/api/status'
        }
    }
};

// 获取当前环境
// 优先级：window.APP_ENV > meta标签 > 默认值
function getEnvironment() {
    // 1. 从全局变量获取
    if (window.APP_ENV) {
        return window.APP_ENV;
    }
    
    // 2. 从 meta 标签获取
    const metaEnv = document.querySelector('meta[name="app-env"]');
    if (metaEnv) {
        return metaEnv.getAttribute('content');
    }
    
    // 3. 从 localStorage 获取（用于开发调试）
    const localEnv = localStorage.getItem('APP_ENV');
    if (localEnv) {
        return localEnv;
    }
    
    // 4. 根据 hostname 自动判断
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'development';
    }
    
    // 5. 默认为生产环境
    return 'production';
}

// 当前环境
const CURRENT_ENV = getEnvironment();

// 当前环境的配置
const currentConfig = CONFIG[CURRENT_ENV] || CONFIG.production;

// 导出 API 配置
const API_CONFIG = {
    BASE_URL: currentConfig.API_BASE_URL,
    ENDPOINTS: currentConfig.API_ENDPOINTS,
    ENV: CURRENT_ENV,
    
    // 获取完整的 API URL
    getUrl: function(endpoint) {
        const path = this.ENDPOINTS[endpoint] || endpoint;
        return this.BASE_URL + path;
    },
    
    // 打印当前配置（调试用）
    debug: function() {
        console.log('=== API Configuration ===');
        console.log('Environment:', this.ENV);
        console.log('Base URL:', this.BASE_URL);
        console.log('Endpoints:', this.ENDPOINTS);
        console.log('========================');
    }
};

// 开发模式下打印配置
if (CURRENT_ENV === 'development') {
    API_CONFIG.debug();
}

// 全局暴露配置
window.API_CONFIG = API_CONFIG;
