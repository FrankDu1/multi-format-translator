# URL 配置验证文档

## 当前配置总结 (2026-01-20)

### 1. 本地开发环境 (localhost:5001)
```javascript
hostname: 'localhost' 或 '127.0.0.1'
API_BASE_URL: 'http://localhost:5002/api'

实际调用示例：
- 文本翻译: http://localhost:5002/api/translate/translate-text ✅
- 图片上传: http://localhost:5002/api/upload ✅
- PDF翻译: http://localhost:5002/api/upload ✅
```

### 2. IP地址直连 (如: 192.168.1.100:5001)
```javascript
hostname: IP地址 (符合 /^\d+\.\d+\.\d+\.\d+$/)
API_BASE_URL: 'http://192.168.1.100:5002/api'

实际调用示例：
- 文本翻译: http://192.168.1.100:5002/api/translate/translate-text ✅
- 图片上传: http://192.168.1.100:5002/api/upload ✅
- PDF翻译: http://192.168.1.100:5002/api/upload ✅
```

### 3. 生产环境 - 域名访问 (offerupup.cn/trans)
```javascript
hostname: 'offerupup.cn'
pathname: '/trans/...'
API_BASE_URL: '/translator-api/api'

实际调用示例：
- 文本翻译: /translator-api/api/translate/translate-text
- 图片上传: /translator-api/api/upload
- PDF翻译: /translator-api/api/upload

Nginx 配置 (nginx-proxy.conf):
location /translator-api/api/ {
    rewrite ^/translator-api/api/(.*)$ /api/$1 break;
    proxy_pass http://localhost:5002;
}

URL 转换过程：
浏览器请求: /translator-api/api/translate/translate-text
Nginx rewrite: /api/translate/translate-text
Flask 收到: /api/translate/translate-text ✅
```

### 4. 生产环境 - 根路径访问 (offerupup.cn/)
```javascript
hostname: 'offerupup.cn'
pathname: '/' 或 '/index.html'
API_BASE_URL: '/translator-api/api'

实际调用示例：
- 文本翻译: /translator-api/api/translate/translate-text
- 图片上传: /translator-api/api/upload
- PDF翻译: /translator-api/api/upload

Nginx 配置同上 ✅
```

## 核心代码逻辑

### env-config.js
```javascript
// 本地环境
if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return {
        API_BASE_URL: 'http://localhost:5002/api',  // ✅ 完整URL
        BASE_PATH: detectedBasePath,
        isProduction: false
    };
}

// IP地址访问
if (ipPattern.test(hostname)) {
    return {
        API_BASE_URL: `http://${hostname}:5002/api`,  // ✅ 完整URL
        BASE_PATH: detectedBasePath,
        isProduction: false
    };
}

// 域名访问（生产）
return {
    API_BASE_URL: '/translator-api/api',  // ✅ 相对路径
    BASE_PATH: detectedBasePath,
    isProduction: true
};
```

### getApiUrl() 方法
```javascript
ENV_CONFIG.getApiUrl = function(endpoint) {
    if (!endpoint) {
        return this.API_BASE_URL;
    }
    const cleanEndpoint = endpoint.replace(/^\//, '');  // 移除开头的 /
    return `${this.API_BASE_URL}/${cleanEndpoint}`;
};
```

### 调用示例
```javascript
// app.js 中的调用
fetch(`${ENV_CONFIG.getApiUrl()}/translate/translate-text`, { ... })

// 实际生成的URL:
// 本地: http://localhost:5002/api/translate/translate-text
// 生产: /translator-api/api/translate/translate-text
```

## Nginx 配置要求

### 方式1: nginx-proxy.conf (当前推荐)
```nginx
location /translator-api/api/ {
    rewrite ^/translator-api/api/(.*)$ /api/$1 break;
    proxy_pass http://localhost:5002;
}
```

### 方式2: nginx-config-update.conf (需要修改前端)
```nginx
location /translator-api/ {
    proxy_pass http://localhost:5002/;  # 注意末尾的 /
}
```
如果使用此配置，需要修改 env-config.js:
```javascript
API_BASE_URL: '/translator-api/api'  // 保持不变
```

## 测试清单

### ✅ 本地开发测试
1. 启动后端: `cd translator_api && python app.py`
2. 启动前端: `cd translator_frontend && python -m http.server 5001`
3. 访问: http://localhost:5001
4. 测试文本翻译
5. 测试图片上传
6. 测试PDF翻译

### ✅ 生产环境测试
1. 确认 Nginx 配置已加载 (nginx-proxy.conf)
2. 访问: https://offerupup.cn/trans
3. 打开浏览器控制台，查看 ENV_CONFIG 日志
4. 测试文本翻译 (检查 Network 标签)
5. 测试图片上传
6. 测试PDF翻译

## 常见错误排查

### 错误1: POST /translator-api/translate/xxx 404
**原因**: API_BASE_URL 缺少 `/api`
**解决**: 确认 API_BASE_URL 为 `/translator-api/api`

### 错误2: POST /translator-api/api/translate/xxx 500
**原因**: Nginx 配置不正确或后端服务未启动
**解决**: 
1. 检查 `nginx -t` 配置是否正确
2. 检查 `systemctl status translator-api` 服务状态
3. 检查后端日志 `logs/app.log`

### 错误3: CORS 错误
**原因**: Nginx 未配置 CORS 或后端未启用
**解决**: 
1. 确认 Nginx 配置包含 CORS headers
2. 确认 config.py 中 ALLOWED_ORIGINS 包含前端域名

## 最终确认

✅ **本地环境**: 直接访问 `http://localhost:5002/api/*`
✅ **IP访问**: 直接访问 `http://IP:5002/api/*`
✅ **生产环境**: Nginx代理 `/translator-api/api/*` → `http://localhost:5002/api/*`

**配置文件**: env-config.js ✅ (已修复)
**Nginx配置**: nginx-proxy.conf ✅ (已验证)
**后端路由**: app.py (Flask Blueprint 注册在 `/api` 路径) ✅
