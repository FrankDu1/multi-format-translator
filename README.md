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

### Windows 安装和启动

1. **克隆项目**
```bash
git clone https://github.com/yourusername/translator.git
cd translator/trans_web_app
```

2. **创建虚拟环境** (推荐)
```bash
python -m venv venv
venv\Scripts\activate
```

3. **安装依赖**
```bash
# OCR服务
cd ocr
pip install -r requirements.txt
cd ..

# Inpaint服务
cd inpaint
pip install -r requirements.txt
cd ..

# API服务
cd translator_api
pip install -r requirements.txt
cd ..
```

4. **配置环境变量**
```bash
# 复制配置文件并根据需要修改
cp translator_api/.env.example translator_api/.env
cp translator_frontend/.env.example translator_frontend/.env
```

5. **启动所有服务**
```bash
# 使用管理脚本启动
manage-services.bat

# 或者手动启动每个服务：
# OCR服务
cd ocr && python app.py

# Inpaint服务  
cd inpaint && python app.py

# API服务
cd translator_api && python app.py

# 前端服务
cd translator_frontend && python -m http.server 5001
```

6. **访问应用**

打开浏览器访问：`http://localhost:5001`

### Linux/Mac 安装和启动

1. **克隆项目**
```bash
git clone https://github.com/yourusername/translator.git
cd translator/trans_web_app
```

2. **使用启动脚本**
```bash
# 启动所有服务
chmod +x start-all-dev.sh
./start-all-dev.sh

# 停止所有服务
chmod +x stop-all-dev.sh
./stop-all-dev.sh
```

## 🔧 服务配置 / Service Configuration

### 服务端口 / Service Ports

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端服务 | 5001 | 静态文件服务器 |
| API服务 | 29003 | 翻译API主服务 |
| OCR服务 | 29001 | 文字识别服务 |
| Inpaint服务 | 29002 | 图像修复服务 |

### 环境变量配置 / Environment Variables

#### API服务 (translator_api/.env)

```bash
# OCR服务地址
OCR_SERVICE_URL=http://localhost:29001/ocr

# Inpaint服务地址
INPAINT_SERVICE_URL=http://localhost:29002/inpaint

# Flask配置
FLASK_HOST=0.0.0.0
FLASK_PORT=29003
FLASK_DEBUG=false

# 翻译模型
NLLB_MODEL=facebook/nllb-200-distilled-600M

# HuggingFace镜像
HF_ENDPOINT=https://hf-mirror.com
```

#### 前端服务 (translator_frontend/.env)

```bash
# API基础URL
API_BASE_URL=http://localhost:29003/api

# 环境
APP_ENV=production

# 应用版本
VERSION=3.0.0
```

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

- Email: offerupup@offerupup.cn
- Website: https://offerupup.cn
- 小红书: [@乐家](https://www.xiaohongshu.com/user/profile/64f2bd6300000000060303f3)

## 🔗 相关链接 / Links

- [在线演示](https://offerupup.cn/trans)
- [文档中心](https://offerupup.cn/docs)
- [问题反馈](https://github.com/yourusername/translator/issues)

---

**如果这个项目对您有帮助，请给个 ⭐ Star！**

**If this project helps you, please give it a ⭐ Star!**
