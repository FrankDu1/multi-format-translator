/**
 * Environment Configuration Loader
 * Automatically detects base path and API endpoints
 * Works with any domain and any base path (/, /trans, /translator, etc.)
 */

const ENV_CONFIG = (() => {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    const origin = window.location.origin;
    
    console.log('🔍 环境检测:', { hostname, pathname, origin });
    
    /**
     * 自动检测基础路径
     * 例如：
     *   - https://example.com/ → BASE_PATH = ''
     *   - https://example.com/trans → BASE_PATH = '/trans'
     *   - https://example.com/translator → BASE_PATH = '/translator'
     */
    function detectBasePath() {
        // 从 pathname 中提取第一级路径
        const match = pathname.match(/^\/([^\/]+)/);
        
        // 如果没有子路径，或者是根路径的文件（如 /index.html）
        if (!match || pathname === '/' || pathname.match(/^\/(index\.html|favicon\.ico)/)) {
            return '';
        }
        
        const firstPath = match[1];
        
        // 排除常见的文件扩展名（说明是根路径下的文件）
        if (firstPath.match(/\.(html|htm|php|jsp)$/i)) {
            return '';
        }
        
        // 返回第一级路径作为 BASE_PATH
        return `/${firstPath}`;
    }
    
    const detectedBasePath = detectBasePath();
    console.log('📍 检测到基础路径:', detectedBasePath || '(根路径)');
    
    // 本地开发环境
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        console.log('✅ 本地开发环境');
        return {
            API_BASE_URL: 'http://localhost:5002/api',
            BASE_PATH: detectedBasePath,
            isProduction: false
        };
    }
    
    // IP 地址访问（Docker 直连测试）
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (ipPattern.test(hostname)) {
        const apiPort = '5002';
        console.log('✅ IP 地址访问（测试环境）');
        return {
            API_BASE_URL: `http://${hostname}:${apiPort}/api`,
            BASE_PATH: detectedBasePath,
            isProduction: false
        };
    }
    
    // 域名访问（生产环境）
    console.log('✅ 域名访问（生产环境）');
    
    // 根据是否有 BASE_PATH 决定 API 路径
    if (detectedBasePath) {
        // 有基础路径（如 /trans）→ 使用 nginx 代理
        console.log('🔄 使用 nginx 反向代理路径');
        return {
            API_BASE_URL: '/translator-api/api',  // ✅ 完整路径，包含 /api
            BASE_PATH: detectedBasePath,
            isProduction: true
        };
    } else {
        // 根路径 → 直接访问
        console.log('🔄 根路径直接访问');
        return {
            API_BASE_URL: '/translator-api/api',  // ✅ 完整路径，包含 /api
            BASE_PATH: '',
            isProduction: true
        };
    }
})();

/**
 * 设置 HTML <base> 标签
 * 自动处理所有相对路径（link, script, img, a 等）
 */
function setBasePath() {
    if (!ENV_CONFIG.BASE_PATH) {
        console.log('⏭️  根路径模式，无需设置 <base> 标签');
        return;
    }
    
    // 检查是否已经有 <base> 标签
    let baseTag = document.querySelector('base');
    
    if (!baseTag) {
        baseTag = document.createElement('base');
        const head = document.head || document.getElementsByTagName('head')[0];
        head.insertBefore(baseTag, head.firstChild);
    }
    
    // 设置 base href（必须以 / 结尾）
    const baseHref = `${window.location.origin}${ENV_CONFIG.BASE_PATH}/`;
    baseTag.setAttribute('href', baseHref);
    
    console.log('✅ 已设置 <base> 标签:', baseHref);
}

/**
 * 获取 API 完整 URL
 */
ENV_CONFIG.getApiUrl = function(endpoint) {
    // 如果没有传入 endpoint，直接返回 API_BASE_URL
    if (!endpoint) {
        return this.API_BASE_URL;
    }
    const cleanEndpoint = endpoint.replace(/^\//, '');
    return `${this.API_BASE_URL}/${cleanEndpoint}`;
};

/**
 * 获取静态资源 URL（保留用于特殊情况）
 */
ENV_CONFIG.getStaticUrl = function(path) {
    // 绝对 URL，直接返回
    if (path.match(/^(https?:)?\/\//)) {
        return path;
    }
    
    const cleanPath = path.replace(/^\//, '');
    
    if (this.BASE_PATH) {
        return `${this.BASE_PATH}/${cleanPath}`;
    }
    
    return `/${cleanPath}`;
};

/**
 * 调试信息
 */
ENV_CONFIG.debug = function() {
    console.group('🔧 ENV_CONFIG Debug');
    console.log('🌐 Location:', {
        hostname: window.location.hostname,
        pathname: window.location.pathname,
        origin: window.location.origin
    });
    console.log('⚙️  Config:', {
        API_BASE_URL: this.API_BASE_URL,
        BASE_PATH: this.BASE_PATH,
        isProduction: this.isProduction
    });
    console.log('📝 Examples:', {
        'API URL': this.getApiUrl('translate/image'),
        'Static URL': this.getStaticUrl('static/js/app.js')
    });
    console.groupEnd();
};

// 初始化时自动执行
if (typeof document !== 'undefined') {
    // 调试输出
    ENV_CONFIG.debug();
    // 设置base路径
    setBasePath();
}

// 导出全局变量
if (typeof window !== 'undefined') {
    window.ENV_CONFIG = ENV_CONFIG;
}