# 🚀 Image Translator API

纯后端 REST API 服务，提供图片翻译功能。

## ✨ 特性

- 🔤 **OCR 识别** - 自动识别图片中的文字
- 🌍 **AI 翻译** - 基于 Meta NLLB-200 模型
- 🎨 **文字移除** - Inpaint 智能去除原文字
- 🖼️ **文字重绘** - 在原位置重绘翻译文字
- 🚀 **GPU 加速** - CUDA GPU 支持
- 📊 **完整日志** - 详细的请求和性能日志
- 🔐 **CORS 支持** - 允许跨域访问

## 🏗️ 架构

这是一个**纯后端 API 服务**，不包含前端界面。

```
客户端 (Web/Mobile/Desktop)
       ↓
   REST API
       ↓
OCR → NLLB → Inpaint → 返回结果
```

## 📋 API 文档

### Base URL
```
http://localhost:5001
```

### 端点列表

#### 1. API 信息
```bash
GET /api/info
```

**响应：**
```json
{
  "api": "Image Translator",
  "version": "2.0",
  "status": "running",
  "services": {
    "ocr": "http://47.97.97.198:29001/ocr",
    "inpaint": "http://localhost:29002/inpaint",
    "translator": "NLLB-200 (Meta)"
  }
}
```

#### 2. 健康检查
```bash
GET /api/health
```

**响应：**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-16T12:00:00",
  "services": {
    "ocr": "configured",
    "inpaint": "enabled",
    "translator": "ready"
  }
}
```

#### 3. 翻译图片 ⭐
```bash
POST /api/translate/image
Content-Type: multipart/form-data

Parameters:
  - file: 图片文件 (required)
  - src_lang: 源语言 'zh' | 'en' (default: 'zh')
  - tgt_lang: 目标语言 'zh' | 'en' (default: 'en')
```

**示例：**
```bash
curl -X POST http://localhost:5001/api/translate/image \
  -F "file=@test.jpg" \
  -F "src_lang=zh" \
  -F "tgt_lang=en"
```

**响应：**
```json
{
  "success": true,
  "output_image": "/api/files/translated_20250101_120000_test.jpg",
  "input_image": "/api/files/20250101_120000_test.jpg",
  "message": "翻译成功",
  "src_lang": "zh",
  "tgt_lang": "en",
  "elapsed_time": "3.45s"
}
```

#### 4. 下载文件
```bash
GET /api/files/<filename>
```

获取翻译后的图片文件。

## 🚀 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python app.py

# 3. 测试 API
curl http://localhost:5001/api/health
```

### Docker 部署 (GPU)

**方式 1: 使用默认配置**
```bash
docker-compose up -d
```

**方式 2: 使用 .env 文件（推荐）**
```bash
# 1. 复制环境变量模板
cp .env.docker .env

# 2. 编辑 .env 修改配置
nano .env

# 3. 启动服务
docker-compose up -d
```

**方式 3: 命令行传参**
```bash
# 自定义端口和配置
HOST_PORT=8080 FLASK_PORT=8080 USE_INPAINT=false docker-compose up -d
```

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

📖 **详细 Docker 部署指南**: 查看 [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

## ⚙️ 配置

本项目支持**环境变量**和 **config.py** 两种配置方式。

### 快速配置

**方式 1: 使用默认配置**（最简单）
```bash
python app.py
```

**方式 2: 环境变量覆盖**（推荐）
```powershell
# Windows PowerShell
$env:FLASK_PORT=8000
$env:USE_INPAINT="false"
python app.py
```

```bash
# Linux/Mac
export FLASK_PORT=8000
export USE_INPAINT=false
python app.py
```

**方式 3: 修改 config.py**
```python
# config.py
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 29003
OCR_SERVICE_URL = "http://47.97.97.198:29001/ocr"
INPAINT_SERVICE_URL = "http://localhost:29002/inpaint"
USE_INPAINT = True
```

📖 **详细配置指南**: 查看 [CONFIG_GUIDE.md](CONFIG_GUIDE.md) 了解所有配置项和使用场景

## 🔒 CORS 配置

默认允许所有域名访问。生产环境请修改 `app.py`：

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-frontend-domain.com"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

## 📊 性能

### GPU 加速
- OCR 识别: ~0.5s
- NLLB 翻译: ~1.5s (GPU) vs ~8s (CPU)
- Inpaint 处理: ~1s
- 总计: **~3.2s (GPU)** vs ~10s (CPU)

## 🧪 测试

```bash
# 健康检查
curl http://localhost:5001/api/health

# 翻译测试
curl -X POST http://localhost:5001/api/translate/image \
  -F "file=@test.jpg" \
  -F "src_lang=zh" \
  -F "tgt_lang=en"
```

## 📂 项目结构

```
translator_api/
├── app.py                    # API 主应用
├── config.py                 # 配置文件
├── logger_config.py          # 日志配置
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 配置
├── docker-compose.yml        # Docker Compose
├── services/                 # 服务模块
│   ├── ocr_service.py       # OCR 客户端
│   ├── nllb_translator_pipeline.py  # NLLB 翻译
│   └── image_translator.py  # 主翻译流程
├── uploads/                  # 上传文件目录
├── logs/                     # 日志目录
└── models/                   # 模型缓存目录
```

## 🐛 故障排查

### 查看日志
```bash
tail -f logs/app.log
tail -f logs/api.log
```

### 常见问题
- **CORS 错误**: 检查 CORS 配置
- **模型下载慢**: 使用 `HF_ENDPOINT=https://hf-mirror.com`
- **GPU 不可用**: 检查 NVIDIA 驱动和 Docker GPU 支持

## 📝 相关项目

- **前端项目**: `translator_frontend` - Web 用户界面
- **完整项目**: `translator_web` - 原始单体应用

## 📄 许可证

MIT License

---

**纯 API 服务，专注后端翻译引擎** 🚀
