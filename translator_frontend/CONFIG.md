# 📚 配置文档完整指南

## 🎯 配置概览

本项目使用 `.env` 文件管理配置，这是前端项目的 **Best Practice**。

### 为什么使用 .env？

✅ **简单** - 一个文件管理所有配置  
✅ **安全** - 敏感信息不提交到 Git  
✅ **灵活** - 支持多环境配置  
✅ **标准** - 业界通用做法  
✅ **易维护** - 无需修改代码  

---

## 📁 配置文件说明

```
.env                    # 当前使用的配置（自己创建，不提交到 Git）
.env.example            # 配置模板（提交到 Git）
.env.development        # 开发环境配置（可选，提交到 Git）
.env.production         # 生产环境配置（可选，提交到 Git）
```

### `.env` - 当前配置

```bash
API_BASE_URL=https://chat.offerupup.cn/trans-service
APP_ENV=production
VERSION=3.0.0
APP_NAME=Image Translator
```

### `.env.example` - 配置模板

提供给团队成员参考，包含所有可用的配置项和说明。

### `.env.development` - 开发环境

```bash
API_BASE_URL=http://localhost:5000
APP_ENV=development
```

### `.env.production` - 生产环境

```bash
API_BASE_URL=https://chat.offerupup.cn/trans-service
APP_ENV=production
```

---

## ⚙️ 配置项说明

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `API_BASE_URL` | 后端 API 地址 | `http://localhost:5000` | `https://api.example.com` |
| `APP_ENV` | 运行环境 | `development` | `production` / `docker` |
| `VERSION` | 应用版本 | `3.0.0` | `3.1.0` |
| `APP_NAME` | 应用名称 | `Image Translator` | 自定义名称 |
| `API_KEY` | API 密钥（可选） | - | `your-api-key` |

---

## 🔄 配置优先级

当有多个配置来源时，按以下优先级加载（从高到低）：

```
1. localStorage (浏览器)      ← 最高优先级（用户自定义）
   ↓
2. HTML meta 标签              ← Docker 注入
   ↓
3. .env 文件                   ← 默认配置
   ↓
4. 代码默认值                  ← 兜底
```

### 示例：

```javascript
// 1. 用户在浏览器控制台设置（最高优先级）
localStorage.setItem('API_BASE_URL', 'https://custom-api.com');

// 2. Docker 注入到 HTML
<meta name="env:API_BASE_URL" content="https://docker-api.com">

// 3. .env 文件
API_BASE_URL=https://file-api.com

// 4. 代码默认值
API_BASE_URL: 'http://localhost:5000'

// 最终使用：https://custom-api.com (localStorage 优先级最高)
```

---

## 🚀 使用方法

### 初始化配置

```bash
# 1. 复制模板
cp .env.example .env

# 2. 编辑配置
nano .env  # 或使用你喜欢的编辑器

# 3. 启动服务
docker-compose up -d
```

### 切换环境

```bash
# 切换到开发环境
cp .env.development .env
docker-compose restart

# 切换到生产环境
cp .env.production .env
docker-compose restart
```

### 临时测试（无需重启）

在浏览器控制台（F12）：

```javascript
// 临时修改 API 地址
ENV_CONFIG.set('API_BASE_URL', 'https://test-api.com');
location.reload();

// 查看当前配置
ENV_CONFIG.debug();

// 恢复默认
ENV_CONFIG.clear();
location.reload();
```

---

## 🐳 Docker 集成

### Dockerfile 自动注入

项目的 Dockerfile 会在容器启动时自动将 `.env` 中的变量注入到 HTML：

```dockerfile
# 复制环境变量注入脚本
COPY inject-env.sh /docker-entrypoint.d/40-inject-env.sh
RUN chmod +x /docker-entrypoint.d/40-inject-env.sh
```

### docker-compose.yml 配置

```yaml
services:
  frontend:
    build: .
    env_file:
      - .env  # 自动加载 .env 文件
```

### 构建时覆盖环境变量

```bash
# 通过命令行覆盖
docker-compose up -d \
  -e API_BASE_URL=https://new-api.com \
  -e APP_ENV=production

# 或使用不同的 env 文件
docker-compose --env-file .env.production up -d
```

---

## 🔍 调试与检查

### 检查当前配置

浏览器控制台（F12）：

```javascript
ENV_CONFIG.debug();
```

输出示例：
```
🔍 ===== Environment Configuration =====
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 API_BASE_URL: https://chat.offerupup.cn/trans-service
🌍 APP_ENV: production
📦 VERSION: 3.0.0
🏷️  APP_NAME: Image Translator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 查看 Docker 注入的环境变量

```bash
# 查看容器日志
docker logs translator-frontend

# 应该看到类似输出：
# 🔧 Starting environment injection...
# 📝 Environment variables:
#    API_BASE_URL: https://chat.offerupup.cn/trans-service
#    APP_ENV: production
```

### 检查 HTML 中的 meta 标签

浏览器开发者工具 → Elements → 查看 `<head>` 部分：

```html
<meta name="env:API_BASE_URL" content="https://chat.offerupup.cn/trans-service">
<meta name="env:APP_ENV" content="production">
```

---

## 🛠️ 常见场景

### 场景 1: 本地开发

```bash
# .env
API_BASE_URL=http://localhost:5000
APP_ENV=development
```

### 场景 2: Docker 部署（前后端分离）

```bash
# .env
API_BASE_URL=https://chat.offerupup.cn/trans-service
APP_ENV=production
```

### 场景 3: 多个开发者共同开发

每个开发者创建自己的 `.env.local`：

```bash
# .env.local (不提交到 Git)
API_BASE_URL=http://192.168.1.100:5000
APP_ENV=development
```

然后在 docker-compose.yml 中：

```yaml
env_file:
  - .env
  - .env.local  # 覆盖 .env 中的配置
```

### 场景 4: CI/CD 自动部署

在 CI/CD pipeline 中动态创建 `.env`：

```bash
# GitHub Actions / GitLab CI
echo "API_BASE_URL=$API_URL" > .env
echo "APP_ENV=production" >> .env
docker-compose up -d --build
```

---

## ⚠️ 安全注意事项

### ✅ 务必做到：

1. **不要提交 `.env` 到 Git**
   ```bash
   # .gitignore 已包含
   .env
   .env.local
   ```

2. **使用 `.env.example` 作为模板**
   - 提交到 Git
   - 不包含敏感信息
   - 提供配置说明

3. **生产环境使用 HTTPS**
   ```bash
   API_BASE_URL=https://api.example.com  # ✅
   API_BASE_URL=http://api.example.com   # ❌
   ```

4. **API 密钥存储在 .env**
   ```bash
   API_KEY=your-secret-key
   ```

### ❌ 避免：

- ❌ 硬编码 API 地址在代码中
- ❌ 在公开仓库提交 `.env`
- ❌ 在代码中暴露敏感信息
- ❌ 使用明文传输（HTTP）

---

## 📖 API 参考

### ENV_CONFIG 对象

```javascript
// 加载配置
await ENV_CONFIG.load();

// 获取配置
ENV_CONFIG.get('API_BASE_URL');
ENV_CONFIG.getApiUrl();
ENV_CONFIG.getEnv();
ENV_CONFIG.getVersion();
ENV_CONFIG.getAppName();

// 设置配置
ENV_CONFIG.set('API_BASE_URL', 'https://new-api.com');

// 环境检查
ENV_CONFIG.isProduction();  // true/false
ENV_CONFIG.isDevelopment(); // true/false

// 调试
ENV_CONFIG.debug();

// 清除配置
ENV_CONFIG.clear();

// 导出 JSON
ENV_CONFIG.toJSON();
```

---

## 🔧 故障排查

### 问题 1: 修改 .env 后没生效

**原因**: Docker 容器没有重新构建

**解决**:
```bash
docker-compose down
docker-compose up -d --build
```

### 问题 2: API 连接失败

**检查步骤**:
```bash
# 1. 查看当前配置
浏览器控制台: ENV_CONFIG.debug()

# 2. 测试 API 连接
curl https://chat.offerupup.cn/trans-service/health

# 3. 查看容器日志
docker logs translator-frontend
```

### 问题 3: CORS 错误

**原因**: 后端 API 未配置 CORS

**解决**: 确保后端配置：
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### 问题 4: localStorage 覆盖了配置

**解决**:
```javascript
// 清除 localStorage
ENV_CONFIG.clear();
location.reload();
```

---

## 📚 相关文档

- [快速开始](QUICKSTART.md)
- [README](README.md)
- [Docker 部署](docker-compose.yml)

---

**Best Practice: 使用 .env 文件管理配置** 🎯
