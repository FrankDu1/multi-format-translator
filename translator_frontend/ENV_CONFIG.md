# 翻译工具前端 - 环境配置说明

本项目支持多环境配置，可以灵活地在不同环境下使用不同的 API 后端。

## 环境类型

### 1. Development（开发环境）
- **API 地址**: `http://localhost:5000`
- **适用场景**: 本地开发，后端服务运行在本机
- **配置方式**: 在 HTML 的 meta 标签中设置 `content="development"`

### 2. Docker（Docker Compose 环境）
- **API 地址**: `http://backend:5000` (使用 Docker 内部网络)
- **适用场景**: 使用 Docker Compose 同时运行前后端
- **配置方式**: 通过环境变量 `APP_ENV=docker`

### 3. Production（生产环境）
- **API 地址**: 使用相对路径，通过 Nginx 反向代理
- **适用场景**: 生产部署，前后端通过 Nginx 统一入口
- **配置方式**: 通过环境变量 `APP_ENV=production`

## 使用方法

### 方法 1: 直接运行（开发模式）

直接在浏览器中打开 `index_original.html`，默认使用 development 配置。

```bash
# 修改 index_original.html 中的 meta 标签
<meta name="app-env" content="development">
```

### 方法 2: Docker Compose（推荐）

#### 生产环境（默认）
```bash
docker-compose up -d --build
```

#### 开发环境（支持热更新）
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

### 方法 3: 使用 localStorage 临时切换环境（调试用）

在浏览器控制台中执行：
```javascript
// 切换到开发环境
localStorage.setItem('APP_ENV', 'development');

// 切换到 Docker 环境
localStorage.setItem('APP_ENV', 'docker');

// 切换到生产环境
localStorage.setItem('APP_ENV', 'production');

// 查看当前配置
API_CONFIG.debug();

// 清除设置
localStorage.removeItem('APP_ENV');
```

## 自定义 API 配置

编辑 `static/js/config.js` 文件，修改对应环境的配置：

```javascript
const CONFIG = {
    development: {
        API_BASE_URL: 'http://localhost:5000',  // 修改为你的开发环境地址
        API_ENDPOINTS: {
            UPLOAD: '/upload',
            TRANSLATE_TEXT: '/translate-text',
            // ...
        }
    },
    // ...
};
```

## 端口配置

当前配置的端口为 **5001**，可以在以下文件中修改：

1. `nginx.conf` - Nginx 监听端口
2. `docker-compose.yml` - Docker 端口映射
3. `Dockerfile` - EXPOSE 声明

## 环境变量

Docker Compose 支持通过环境变量设置：

```yaml
environment:
  - APP_ENV=docker  # development | docker | production
```

或者使用 `.env` 文件：
```bash
APP_ENV=docker
```

## 调试

在浏览器控制台中查看当前配置：
```javascript
API_CONFIG.debug();
```

输出示例：
```
=== API Configuration ===
Environment: docker
Base URL: http://backend:5000
Endpoints: {UPLOAD: "/upload", TRANSLATE_TEXT: "/translate-text", ...}
========================
```

## 常见问题

### Q: 如何知道当前使用的是哪个环境？
A: 打开浏览器控制台，输入 `API_CONFIG.ENV` 查看。

### Q: 修改了配置但没有生效？
A: 清除浏览器缓存，或者强制刷新（Ctrl+F5）。

### Q: Docker 环境下无法连接后端？
A: 确保：
1. 后端服务名称为 `backend`
2. 前后端在同一个 Docker 网络中
3. 后端服务监听在 `0.0.0.0:5000` 而不是 `127.0.0.1:5000`

## 更新日志

- 2025-10-16: 添加多环境配置支持
- 2025-10-16: 修改端口为 5001
- 2025-10-16: 使用中国镜像源加速构建
