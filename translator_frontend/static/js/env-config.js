/**
 * Environment Configuration Loader
 * Loads configuration from .env, meta tags, or localStorage
 * 
 * Usage:
 *   await ENV_CONFIG.load();
 *   const apiUrl = ENV_CONFIG.getApiUrl();
 *   ENV_CONFIG.debug();
 */

const ENV_CONFIG = {
    // ✅ 立即可用的默认配置（同步）
    API_BASE_URL: (() => {
        // 检查是否在环境变量中配置了 API 地址
        if (window.ENV && window.ENV.API_BASE_URL) {
            return window.ENV.API_BASE_URL;
        }
        
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:5002/api';
        } else {
            // 生产环境：使用域名 + API 端口
            return window.location.protocol + '//' + hostname + ':5002/api';
        }
    })(),
    APP_ENV: window.location.hostname === 'localhost' ? 'development' : 'production',
    VERSION: '3.0.0',
    APP_NAME: 'Image Translator',
    
    // 异步初始化：尝试从 .env 文件加载（可选覆盖）
    async init() {
        console.log('📍 默认配置（根据域名）:', {
            hostname: window.location.hostname,
            API_BASE_URL: this.API_BASE_URL,
            APP_ENV: this.APP_ENV
        });
        
        await this.loadEnvFile();
        
        console.log('✅ 最终配置:', {
            API_BASE_URL: this.API_BASE_URL,
            APP_ENV: this.APP_ENV,
            VERSION: this.VERSION
        });
    },
    
    // 从 .env 文件加载配置（可选）
    async loadEnvFile() {
        try {
            console.log('🔍 尝试加载 .env 文件...');
            const response = await fetch('/.env', { cache: 'no-cache' });
            
            if (!response.ok) {
                console.log('ℹ️ .env 文件不存在，使用默认配置');
                return false;
            }
            
            const text = await response.text();
            const lines = text.split('\n');
            
            let loadedCount = 0;
            lines.forEach(line => {
                line = line.trim();
                if (line && !line.startsWith('#')) {
                    const [key, ...valueParts] = line.split('=');
                    const value = valueParts.join('=').trim().replace(/^["']|["']$/g, '');
                    
                    if (key && value) {
                        this[key.trim()] = value;
                        loadedCount++;
                    }
                }
            });
            
            console.log(`✅ .env 文件已加载 (${loadedCount} 个配置)`);
            return true;
            
        } catch (error) {
            console.log('ℹ️ 无法加载 .env 文件:', error.message);
            return false;
        }
    },
    
    // ✅ 同步获取API地址（立即可用，不需要等待初始化）
    getApiUrl() {
        return this.API_BASE_URL;
    },
    
    getEnv() {
        return this.APP_ENV;
    },
    
    getVersion() {
        return this.VERSION;
    }
};

// 自动初始化（异步，但不影响默认值使用）
(async () => {
    try {
        await ENV_CONFIG.init();
        console.log('🎉 ENV_CONFIG 初始化完成');
    } catch (error) {
        console.error('❌ ENV_CONFIG 初始化失败:', error);
    }
})();
