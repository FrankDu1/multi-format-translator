# 🎨 Image Translator Frontend

独立前端项目，调用 REST API 进行图片翻译。

## ✨ 特性

- 🎯 **纯前端** - 无后端依赖，直接调用 REST API
- 📱 **响应式设计** - 支持桌面和移动端
- ⚙️ **可配置 API** - 支持自定义 API 地址
- 🔄 **实时预览** - 上传即时预览
- 💾 **下载功能** - 一键下载翻译结果
- 🌐 **多语言支持** - 中英文翻译

## 🚀 快速开始

### 方式 1: 直接打开 HTML

```bash
# 直接用浏览器打开
open index.html  # Mac
start index.html # Windows
```

### 方式 2: 使用本地服务器

```bash
# Python
python -m http.server 8080

# Node.js
npx http-server -p 8080

# PHP
php -S localhost:8080
```

访问: http://localhost:8080

### 方式 3: Nginx 部署

```bash
# 使用 Docker + Nginx
docker-compose up -d
```

访问: http://localhost:80

## ⚙️ 配置

### 1. 使用 .env 文件配置（推荐 ⭐）

复制示例配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 API 地址：

```bash
# .env
API_BASE_URL=https://chat.offerupup.cn/trans-service
APP_ENV=production
VERSION=3.0.0
APP_NAME=Image Translator
```

### 2. 配置优先级

配置按以下优先级加载（从高到低）：

1. **浏览器 localStorage** - 用户自定义（最高优先级）
2. **HTML meta 标签** - Docker 注入的环境变量
3. **.env 文件** - 默认配置
4. **代码默认值** - 兜底配置

### 3. 浏览器控制台动态配置

打开浏览器开发者工具（F12），输入：

```javascript
// 修改 API 地址
ENV_CONFIG.set('API_BASE_URL', 'https://your-api.com');
location.reload();

// 查看当前配置
ENV_CONFIG.debug();

// 重置配置
ENV_CONFIG.clear();
location.reload();
```

## 📂 项目结构

```
translator_frontend/
├── index.html              # 主页面
├── static/                 # 静态资源
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       ├── app.js         # 主要逻辑（可选）
│       └── i18n.js        # 国际化
├── nginx.conf              # Nginx 配置
├── Dockerfile              # Docker 配置
├── docker-compose.yml      # Docker Compose
└── README.md               # 本文档
```

## 🐳 Docker 部署

### 使用 Nginx

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 自定义配置

编辑 `nginx.conf` 修改服务器配置。

## 🔧 API 集成

前端调用后端 API 的关键代码：

```javascript
// 翻译图片
async function translateImage() {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('src_lang', 'zh');
    formData.append('tgt_lang', 'en');

    const response = await fetch(`${API_BASE_URL}/api/translate/image`, {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (result.success) {
        displayResult(result);
    }
}
```

## 📡 API 要求

后端 API 必须支持 CORS，并提供以下端点：

- `GET /api/health` - 健康检查
- `POST /api/translate/image` - 翻译图片
- `GET /api/files/<filename>` - 获取文件

## 🎨 自定义样式

编辑 `static/css/style.css` 修改界面样式：

```css
/* 主题颜色 */
:root {
    --primary-color: #4CAF50;
    --secondary-color: #2196F3;
}
```

## 🌍 多域名部署

### 前端部署在不同域名

```
前端: https://translate.example.com
API: https://api.example.com
```

确保 API 配置了正确的 CORS：

```python
# API 端 (app.py)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://translate.example.com"],
        "methods": ["GET", "POST", "OPTIONS"]
    }
})
```

## 📱 移动端适配

页面已经做了响应式设计，在移动端自动适配。

## 🔒 安全建议

1. **HTTPS**: 生产环境使用 HTTPS
2. **API 密钥**: 如果需要，在请求头添加认证
3. **文件大小限制**: 前端验证文件大小
4. **文件类型验证**: 只允许图片文件

## 🧪 测试

### 测试 API 连接

点击页面上的"测试连接"按钮，或手动测试：

```bash
curl http://localhost:5001/api/health
```

### 测试翻译功能

1. 上传测试图片
2. 选择语言
3. 点击"开始翻译"
4. 查看结果

## 📊 性能优化

- ✅ 图片预览使用 FileReader API
- ✅ 异步上传，不阻塞 UI
- ✅ 错误处理和重试机制
- ✅ 加载状态提示

## 🐛 故障排查

### CORS 错误

```
Access to fetch at 'http://localhost:5001/api/translate/image' 
from origin 'http://localhost:8080' has been blocked by CORS policy
```

**解决**: 确保后端 API 配置了 CORS。

### API 连接失败

1. 检查 API 是否运行：`curl http://localhost:5001/api/health`
2. 检查防火墙设置
3. 确认 API 地址配置正确

### 图片无法显示

1. 检查浏览器控制台错误
2. 确认 API 返回的图片路径正确
3. 测试直接访问图片 URL

## 🔄 更新日志

### v2.0.0 (2025-10-16)
- ✨ 前后端完全分离
- ✨ 支持自定义 API 地址
- ✨ 添加 API 连接测试
- ✨ Docker + Nginx 部署支持

## 📝 相关项目

- **API 后端**: `translator_api` - REST API 服务
- **原始项目**: `translator_web` - 单体应用

## 📄 许可证

MIT License

---

**独立前端，灵活部署** 🎨
