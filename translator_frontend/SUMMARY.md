# 环境配置总结

## ✅ 已完成的配置

### 1. 创建了配置管理系统
- ✅ `static/js/config.js` - 集中管理所有 API 配置
- ✅ 支持三种环境：development、docker、production
- ✅ 支持多种配置方式：meta 标签、环境变量、localStorage

### 2. 修改了所有 API 调用
- ✅ 文件上传 API: `/upload` → `API_CONFIG.getUrl('UPLOAD')`
- ✅ 文本翻译 API: `/translate-text` → `API_CONFIG.getUrl('TRANSLATE_TEXT')`
- ✅ PDF 翻译 API: `/upload` → `API_CONFIG.getUrl('TRANSLATE_PDF')`
- ✅ 系统状态 API: `/health` → `API_CONFIG.getUrl('STATUS')`

### 3. 创建了 Docker 配置
- ✅ `Dockerfile` - 支持环境变量注入
- ✅ `docker-entrypoint.sh` - 启动时设置环境
- ✅ `docker-compose.yml` - 生产环境配置 (APP_ENV=docker)
- ✅ `docker-compose.dev.yml` - 开发环境配置（支持热更新）

### 4. 创建了文档
- ✅ `ENV_CONFIG.md` - 详细的环境配置说明
- ✅ `QUICK_START.md` - 快速切换环境指南

## 🎯 使用方法

### 开发模式（本地开发，后端在本机）
```bash
# 方式 1: 直接修改 HTML
# 编辑 index_original.html，设置 <meta name="app-env" content="development">

# 方式 2: 使用 localStorage（推荐，无需重新构建）
# 浏览器控制台: localStorage.setItem('APP_ENV', 'development'); location.reload();

# 方式 3: 使用开发配置启动
docker-compose -f docker-compose.dev.yml up -d --build
```

### Docker Compose 模式（前后端都在容器）
```bash
# 默认配置就是 Docker 模式
docker-compose up -d --build

# API 将指向: http://backend:5000
# 确保你的 docker-compose 中后端服务名为 "backend"
```

### 生产模式（Nginx 反向代理）
```bash
# 修改 docker-compose.yml
environment:
  - APP_ENV=production

docker-compose up -d --build
```

## 📝 配置示例

### config.js 配置结构
```javascript
const CONFIG = {
    development: {
        API_BASE_URL: 'http://localhost:5000',  // ← 修改这里设置开发环境后端地址
        API_ENDPOINTS: {
            UPLOAD: '/upload',
            TRANSLATE_TEXT: '/translate-text',
            // ...
        }
    },
    docker: {
        API_BASE_URL: 'http://backend:5000',  // ← Docker 内部网络地址
        // ...
    },
    production: {
        API_BASE_URL: '',  // ← 使用相对路径，通过 Nginx 代理
        // ...
    }
};
```

### Docker Compose 完整示例（前后端）
```yaml
version: '3.8'

services:
  # 前端
  frontend:
    build: .
    container_name: translator-frontend
    ports:
      - "5001:5001"
    environment:
      - APP_ENV=docker
    networks:
      - app-network

  # 后端（示例）
  backend:
    image: your-backend-image
    container_name: translator-backend
    ports:
      - "5000:5000"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

## 🔍 调试方法

### 查看当前配置
```javascript
// 浏览器控制台
API_CONFIG.debug();

// 输出：
// === API Configuration ===
// Environment: docker
// Base URL: http://backend:5000
// Endpoints: {...}
// ========================
```

### 测试 API 连接
```javascript
// 测试上传 API
console.log('Upload URL:', API_CONFIG.getUrl('UPLOAD'));

// 测试文本翻译 API
console.log('Translate Text URL:', API_CONFIG.getUrl('TRANSLATE_TEXT'));
```

## 🚀 当前状态

- ✅ 容器运行在端口 **5001**
- ✅ 当前环境：**docker**
- ✅ API Base URL: **http://backend:5000**
- ✅ 所有静态资源正确加载（CSS、JS）

## 📌 注意事项

1. **修改配置后需要重新构建**
   ```bash
   docker-compose up -d --build
   ```

2. **使用 localStorage 可以临时切换，无需重新构建**
   ```javascript
   localStorage.setItem('APP_ENV', 'development');
   location.reload();
   ```

3. **后端服务必须监听 0.0.0.0，不能是 127.0.0.1**
   ```python
   # 正确
   app.run(host='0.0.0.0', port=5000)
   
   # 错误（容器内无法访问）
   app.run(host='127.0.0.1', port=5000)
   ```

4. **确保前后端在同一 Docker 网络**
   ```yaml
   networks:
     - app-network  # 前后端使用相同的网络
   ```

## 🎉 完成！

现在你可以灵活地在不同环境下切换 API 配置了！
