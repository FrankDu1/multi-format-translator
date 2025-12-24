[![CI](https://github.com/FrankDu1/multi-format-translator/actions/workflows/ci.yml/badge.svg)](https://github.com/FrankDu1/multi-format-translator/actions)
[![Release](https://img.shields.io/github/v/release/FrankDu1/multi-format-translator)](https://github.com/FrankDu1/multi-format-translator/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/FrankDu1/multi-format-translator?style=social)](https://github.com/FrankDu1/multi-format-translator/stargazers)
[![Demo](https://img.shields.io/badge/demo-online-brightgreen)](https://offerupup.cn/trans)
[![Docker Pulls](https://img.shields.io/docker/pulls/FrankDu1/multi-format-translator)](https://hub.docker.com/r/FrankDu1/multi-format-translator)
[![Coverage](https://img.shields.io/codecov/c/github/FrankDu1/multi-format-translator)](https://codecov.io/gh/FrankDu1/multi-format-translator)


# 🌐 文档翻译工具 / Document Translation Tool

一个功能强大的多格式文档翻译工具，支持PDF、PPT、图片和文本翻译。基于先进的AI技术，提供高质量的翻译服务，同时保持原文档格式。

A powerful multi-format document translation tool supporting PDF, PPT, image, and text translation. Built on advanced AI technology, providing high-quality translation services while preserving original document formatting.

## ✨ 主要特性 / Key Features

- 📄 **PDF翻译** - 保持原文档格式和样式的专业级PDF翻译
- 🖼️ **图片翻译** - 支持JPG、PNG、BMP、TIFF、WebP等多种格式，自动识别和翻译图片中的文字
- 📊 **PPT翻译** - 支持PPTX/PPT格式的幻灯片翻译
- 📝 **文本翻译** - 支持中英文互译，自动检测语言
- 🤖 **AI智能总结** - 可选的AI文档总结功能
- 🌍 **多语言界面** - 支持中文和英文界面切换
- 🎨 **格式保持** - 翻译后保持原文档的格式和样式

## 🏗️ 项目架构 / Architecture

```
trans_web_app/
├── translator_frontend/     # 前端服务 (静态文件服务器)
├── translator_api/          # 翻译API服务 (Flask)
├── ocr/                     # OCR识别服务
├── inpaint/                 # 图像修复服务
├── logs/                    # 日志文件目录
└── manage-services.bat      # Windows服务管理脚本
```

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

- Python 3.8+
- pip
- (可选) CUDA GPU用于加速

### 1. 克隆项目
```bash
git clone https://github.com/FrankDu1/multi-format-translator.git
cd multi-format-translator
```

### 2. 配置环境变量
```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，配置你的服务（默认为 localhost，可直接运行）
# Windows: notepad .env
# Linux/Mac: nano .env
```

### 3. 安装依赖并启动服务

**Windows (推荐使用管理脚本):**
```cmd
manage-services.bat start
```

**Linux/Mac:**
```bash
chmod +x start-all-dev.sh
./start-all-dev.sh
```

**手动启动各服务:**
```bash
# OCR 服务 (端口 8899)
cd ocr && pip install -r requirements.txt && python app.py &

# Inpaint 服务 (端口 8900)
cd inpaint && pip install -r requirements.txt && python app.py &

# API 服务 (端口 5002)
cd translator_api && pip install -r requirements.txt && python app.py &

# 前端 (端口 5001)
cd translator_frontend && python -m http.server 5001
```

### 4. 访问应用
打开浏览器访问：`http://localhost:5001`

---

## 🔧 生产部署 / Production Deployment

### Docker Compose (推荐)
```bash
# 修改 docker-compose.yml 中的环境变量
docker-compose up -d
```

### 环境变量配置
生产环境需要配置：
- `PRODUCTION_URL`: 你的域名
- `PRODUCTION_DOMAIN`: 你的域名（用于 CORS）
- `OPENAI_API_KEY`: OpenAI API 密钥（可选）
- `MONITOR_PASSWORD_HASH`: 监控面板密码哈希

**生成监控密码哈希：**
```bash
python generate_password.py
# 输入密码后，将输出的哈希值添加到 .env 文件
```

## 🔧 配置说明 / Configuration

### 环境变量

所有配置通过 `.env` 文件管理（参考 `.env.example`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `API_HOST` | `0.0.0.0` | API 服务监听地址 |
| `API_PORT` | `5002` | API 服务端口 |
| `OCR_HOST` | `localhost` | OCR 服务地址 |
| `OCR_PORT` | `8899` | OCR 服务端口 |
| `INPAINT_HOST` | `localhost` | Inpaint 服务地址 |
| `INPAINT_PORT` | `8900` | Inpaint 服务端口 |
| `FRONTEND_PORT` | `5001` | 前端端口 |
| `ALLOWED_ORIGINS` | `http://localhost:5001` | CORS 允许的源（逗号分隔）|
| `OPENAI_API_KEY` | - | OpenAI API 密钥（可选）|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 服务地址（可选）|
| `MONITOR_USERNAME` | `admin` | 监控面板用户名 |
| `MONITOR_PASSWORD_HASH` | - | 监控面板密码哈希 |
| `MAX_FILE_SIZE` | `16777216` | 最大文件大小（字节）|
| `PRODUCTION_DOMAIN` | - | 生产环境域名 |

### 服务端口

| 服务 | 默认端口 | 环境变量 |
|------|---------|----------|
| 前端服务 | 5001 | `FRONTEND_PORT` |
| API服务 | 5002 | `API_PORT` |
| OCR服务 | 8899 | `OCR_PORT` |
| Inpaint服务 | 8900 | `INPAINT_PORT` |

## 📖 使用指南 / Usage Guide

### 1. 文本翻译
- 直接在文本框中输入或粘贴要翻译的文本
- 选择源语言和目标语言（支持自动检测）
- 点击"开始翻译"按钮

### 2. PDF翻译
- 点击"PDF翻译"标签
- 选择要翻译的PDF文件
- 设置翻译参数
- 下载翻译后的PDF文件

### 3. 图片翻译
- 点击"图片翻译"标签
- 上传图片文件（支持JPG、PNG、BMP、TIFF、WebP）
- 系统自动识别图片中的文字并翻译
- 查看翻译前后的对比效果

### 4. PPT翻译
- 点击"PPT翻译"标签
- 上传PPTX或PPT文件
- 等待翻译完成
- 下载翻译后的演示文稿

### 5. AI总结功能
- 在翻译设置中开启"AI总结"开关
- 翻译完成后会自动生成文档内容摘要

## 🐳 Docker 部署 / Docker Deployment

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 单独构建镜像

```bash
# API服务
cd translator_api
docker build -t translator-api .

# OCR服务
cd ocr
docker build -t translator-ocr .

# Inpaint服务
cd inpaint
docker build -t translator-inpaint .

# 前端服务
cd translator_frontend
docker build -t translator-frontend .
```

## 🛠️ 开发指南 / Development Guide

### 项目结构

```
trans_web_app/
├── translator_frontend/          # 前端
│   ├── static/
│   │   ├── css/                 # 样式文件
│   │   ├── js/                  # JavaScript文件
│   │   │   ├── app.js          # 主应用逻辑
│   │   │   ├── i18n.js         # 国际化
│   │   │   └── env-config.js   # 环境配置
│   │   └── images/             # 图片资源
│   └── index.html              # 主页面
│
├── translator_api/              # API服务
│   ├── services/               # 业务逻辑
│   │   ├── text_translator.py # 文本翻译
│   │   ├── pdf_translator.py  # PDF翻译
│   │   ├── image_translator.py# 图片翻译
│   │   ├── ppt_translator.py  # PPT翻译
│   │   └── ocr_service.py     # OCR服务封装
│   ├── app.py                 # Flask应用入口
│   └── config.py              # 配置文件
│
├── ocr/                        # OCR服务
│   └── app.py
│
└── inpaint/                    # 图像修复服务
    └── app.py
```

### 添加新功能

1. 在 `translator_api/services/` 中添加新的服务模块
2. 在 `app.py` 中注册新的API路由
3. 在前端 `app.js` 中添加对应的调用逻辑
4. 更新 `i18n.js` 添加多语言支持

### 运行测试

```bash
# API服务测试
cd translator_api
pytest

# OCR服务测试
cd ocr
python test_ocr.py
```

## 📝 API 文档 / API Documentation

### 文本翻译
```
POST /api/translate/text
Content-Type: application/json

{
  "text": "要翻译的文本",
  "source_lang": "en",
  "target_lang": "zh"
}
```

### 图片翻译
```
POST /api/translate/image
Content-Type: multipart/form-data

file: (binary)
source_lang: en
target_lang: zh
```

### PDF翻译
```
POST /api/translate/pdf
Content-Type: multipart/form-data

file: (binary)
source_lang: en
target_lang: zh
```

### PPT翻译
```
POST /api/translate/ppt
Content-Type: multipart/form-data

file: (binary)
source_lang: en
target_lang: zh
```

## 🤝 贡献指南 / Contributing

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证 / License

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢 / Acknowledgments

- [Facebook NLLB](https://github.com/facebookresearch/fairseq/tree/nllb) - 翻译模型
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR引擎
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Ollama](https://ollama.ai/) - AI模型服务

## 📞 联系方式 / Contact

- Email: dusiyu2004@hotmail.com
- Website: https://offerupup.top
- 小红书: [@乐家](https://www.xiaohongshu.com/user/profile/64f2bd6300000000060303f3)

## 🔗 相关链接 / Links

- [在线演示](https://offerupup.cn/trans)
- [文档中心](https://offerupup.cn/docs)
- [问题反馈](https://github.com/FrankDu1/translator/issues)

---

**如果这个项目对您有帮助，请给个 ⭐ Star！**

**If this project helps you, please give it a ⭐ Star!**
