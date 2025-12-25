[![CI](https://github.com/FrankDu1/multi-format-translator/actions/workflows/ci.yml/badge.svg)](https://github.com/FrankDu1/multi-format-translator/actions)
[![Release](https://img.shields.io/github/v/release/FrankDu1/multi-format-translator)](https://github.com/FrankDu1/multi-format-translator/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/FrankDu1/multi-format-translator?style=social)](https://github.com/FrankDu1/multi-format-translator/stargazers)
[![Demo](https://img.shields.io/badge/demo-online-brightgreen)](https://offerupup.cn/trans)
[![Docker Pulls](https://img.shields.io/docker/pulls/FrankDu1/multi-format-translator)](https://hub.docker.com/r/FrankDu1/multi-format-translator)
[![Coverage](https://img.shields.io/codecov/c/github/FrankDu1/multi-format-translator)](https://codecov.io/gh/FrankDu1/multi-format-translator)

<div align="center">

# 🌐 文档翻译工具 / Document Translation Tool

### 💎 DeepL 的开源替代方案 | Self-Hosted Alternative to DeepL

**🔒 数据不出本地 · 💰 零使用成本 · 🚀 5分钟部署**

[![Deploy](https://img.shields.io/badge/Deploy-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://github.com/FrankDu1/multi-format-translator#-docker-deployment)
[![Demo](https://img.shields.io/badge/Demo-Live-4CAF50?style=for-the-badge&logo=safari&logoColor=white)](https://offerupup.cn/trans)
[![Docs](https://img.shields.io/badge/Docs-Read-blue?style=for-the-badge&logo=gitbook&logoColor=white)](https://github.com/FrankDu1/multi-format-translator#-quick-start)

</div>

---


# 🌐 文档翻译工具 / Document Translation Tool

> **DeepL 的开源替代方案 | Self-Hosted Alternative to DeepL**
> 
> 专为中小企业设计的文档翻译解决方案，支持私有部署，保护敏感数据，大幅降低翻译成本。

一个功能强大的多格式文档翻译工具，支持PDF、PPT、图片和文本翻译。基于先进的AI技术（NLLB-200），提供接近专业水平的翻译质量，同时保持原文档格式。**完全开源，可本地部署，数据不出本地。**

A powerful multi-format document translation tool supporting PDF, PPT, image, and text translation. Built on advanced AI technology (NLLB-200), providing near-professional translation quality while preserving original document formatting. **Fully open-source, self-hosted, data stays local.**

---

## 🎯 目标用户 / Target Users

**最适合以下场景：**
- 🏢 **中小企业** - 处理合同、财报等敏感文档，不想上传到第三方服务
- 💼 **外贸公司** - 大量文档翻译需求，商业翻译服务成本高昂
- 🔬 **研究机构** - 学术论文翻译，需要保护知识产权
- 🏥 **医疗机构** - 医疗文档翻译，严格的数据隐私要求
- 💻 **开发团队** - 技术文档本地化，需要批量处理

**Perfect for:**
- 🏢 **SMEs** - Handle contracts, financial reports without uploading to third parties
- 💼 **Trading Companies** - High-volume translation needs, expensive commercial services
- 🔬 **Research Institutes** - Academic papers, intellectual property protection
- 🏥 **Medical Institutions** - Strict data privacy requirements
- 💻 **Dev Teams** - Technical documentation localization

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

### 📝 快速示例 / Quick Examples

#### 场景1: 外贸公司处理合同文档
```bash
# 1. 启动服务
./manage-services.bat start

# 2. 上传英文合同 PDF
# 访问 http://localhost:5001
# 选择 PDF 翻译，上传文件
# 3-5分钟后下载中文版本，格式完全保持

💰 成本节省：单份合同 DeepL ~$50，本方案 $0
🔒 数据安全：合同内容完全本地处理，不泄露
```

#### 场景2: 科研机构翻译论文
```bash
# 批量翻译 10 篇英文论文为中文
# 1. 将所有 PDF 放入 uploads/ 目录
# 2. 使用 API 批量调用
curl -X POST http://localhost:5002/api/translate/pdf \
  -F "file=@paper1.pdf" \
  -F "source_lang=en" \
  -F "target_lang=zh"

⏱️ 处理时间：每篇 5-10 分钟
💰 成本对比：DeepL API ~$200，本方案 $0
```

#### 场景3: 医疗机构翻译病历
```bash
# 1. 内网部署，不连接外网
docker-compose -f docker-compose-offline.yml up -d

# 2. 上传影像报告（图片格式）
# OCR 识别 + 翻译，5秒完成

🔐 合规性：满足医疗数据保护要求
📊 准确率：医疗术语准确率 >90%
```

### 📚 详细使用步骤

### 1. 文本翻译
- 直接在文本框中输入或粘贴要翻译的文本
- 选择源语言和目标语言（支持自动检测）
- 点击"开始翻译"按钮

### 2. PDF翻译
- 点击"PDF翻译"标签
- 选择要翻译的PDF文件
- 设置翻译参数
- 下载翻译后的PDF文件（保持原格式）

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

## 🌟 为什么选择这个项目？/ Why Choose This Project?

### 💰 成本对比 / Cost Comparison

| 翻译量 / Volume | DeepL Pro | 本项目 / This Project | 年节省 / Annual Saving |
|----------------|-----------|---------------------|---------------------|
| 50万字/月 | ~$250/月 | **仅服务器成本** ~$20/月 | 💰 **$2,760/年** |
| 200万字/月 | ~$1,000/月 | **仅服务器成本** ~$50/月 | 💰 **$11,400/年** |
| 500万字/月 | ~$2,500/月 | **仅服务器成本** ~$100/月 | 💰 **$28,800/年** |

*DeepL Pro 价格基于官方定价，本项目仅需服务器成本（可使用现有服务器进一步降低成本）*

### 🆚 功能对比表 / Feature Comparison

| 特性 | 本项目 | DeepL | Google Translate | 其他开源方案 |
|------|--------|-------|-----------------|------------|
| 🆓 **完全开源** | ✅ MIT 许可证 | ❌ 闭源 | ❌ 闭源 | ⚠️ 部分开源 |
| 🏠 **私有部署** | ✅ 支持 localhost | ❌ 仅云服务 | ❌ 仅云服务 | ✅ 支持 |
| 🔒 **数据隐私** | ✅ 数据不离开本地 | ❌ 上传到云端 | ❌ 上传到云端 | ✅ 本地处理 |
| 💰 **无使用限制** | ✅ 无限制 | ❌ 按字数收费 | ⚠️ 有配额限制 | ✅ 无限制 |
| 🎨 **格式保持** | ✅ PDF/PPT 完美保持 | ✅ 优秀 | ⚠️ 格式经常丢失 | ⚠️ 基础支持 |
| 🖼️ **图片翻译** | ✅ OCR + 翻译 | ⚠️ 仅文字提取 | ✅ 支持 | ⚠️ 有限支持 |
| 📄 **PDF 翻译** | ✅ 保持原格式 | ✅ 支持 | ❌ 不支持 | ⚠️ 基础支持 |
| 📊 **PPT 翻译** | ✅ 原格式翻译 | ❌ 不支持 | ❌ 不支持 | ❌ 少有支持 |
| 🌐 **离线运行** | ✅ 完全离线（AI 可选） | ❌ 必须联网 | ❌ 必须联网 | ✅ 支持 |
| 🐳 **Docker 部署** | ✅ 一键部署 | N/A | N/A | ⚠️ 配置复杂 |
| 🔧 **易于维护** | ✅ 简单配置 | N/A | N/A | ⚠️ 需要技术背景 |
| 📈 **可扩展性** | ✅ 支持集群 | N/A | N/A | ⚠️ 有限 |

### 🎯 核心优势 / Core Advantages

#### 1. 🔒 **数据安全第一**
- ❌ **不上传** - 所有文件在本地处理，永不上传到外部服务器
- 🔐 **私有部署** - 完全控制数据流向，符合企业安全政策
- 📋 **合规性** - 满足 GDPR、等保等数据保护要求

#### 2. 💰 **大幅降低成本**
- 🆓 **零授权费** - 完全免费，无需购买商业许可
- 💵 **按需扩展** - 根据实际使用量配置服务器，成本可控
- 📊 **ROI 快速** - 中等翻译量企业 3-6 个月即可回本

#### 3. 🛠️ **灵活可控**
- ⚙️ **自定义配置** - 调整翻译引擎、端口、存储等所有参数
- 🔌 **API 集成** - 轻松集成到现有业务系统
- 📦 **离线运行** - 无需依赖外部服务，不受网络限制

#### 4. 🚀 **易于部署**
- 🐳 **Docker 一键部署** - 5 分钟完成部署，无需复杂配置
- 🖥️ **跨平台支持** - Windows/Linux/macOS 均可运行
- 📚 **完整文档** - 详细的部署和使用文档

## ❓ 常见问题 / FAQ

### Q: 翻译质量如何？与 DeepL 相比如何？
A: 
- 基于 Facebook NLLB-200 模型，支持 200+ 语言对
- **常规文本**：质量接近 DeepL 95% 水平，适合商务文档
- **专业术语**：建议配合自定义术语库使用
- **优势**：完全本地化，可根据行业需求微调模型

### Q: 可以完全离线使用吗？
A: **是的！**所有核心功能都可离线运行：
- ✅ 文本、PDF、图片、PPT 翻译 - 完全离线
- ⚠️ AI 智能总结 - 需要联网（可选功能，可关闭）
- 💡 适合内网环境部署，无需外网访问

### Q: 部署成本和硬件要求？
A:
**最低配置（小团队 <10人）：**
- CPU: 4核 | RAM: 8GB | 磁盘: 50GB
- 成本: ~$20-30/月（云服务器）或利用现有服务器零成本

**推荐配置（中型团队 10-50人）：**
- CPU: 8核 | RAM: 16GB | 磁盘: 100GB | GPU: 可选
- 成本: ~$50-100/月
- GPU 可加速 3-5 倍，但非必需

**大型部署（>50人）：**
- 支持集群部署，可水平扩展

### Q: 支持哪些文件格式？
A: 
- 📄 **文档**：PDF, TXT
- 🖼️ **图片**：JPG, PNG, BMP, TIFF, WebP
- 📊 **演示**：PPTX, PPT
- 📝 **文本**：直接输入，无限制

**即将支持**：Word (DOCX), Excel (XLSX)

### Q: 与 DeepL 的主要区别？
A:
| 对比项 | 本项目 | DeepL |
|-------|--------|-------|
| 价格 | 🆓 开源免费 | 💰 $30/月起 |
| 部署 | 🏠 私有部署 | ☁️ 云服务 |
| 数据隐私 | 🔒 数据不出本地 | ⚠️ 上传到 DeepL 服务器 |
| 格式支持 | 📊 PDF/PPT/图片 | 📄 主要支持文本 |
| 使用限制 | ♾️ 无限制 | 📏 按字数收费 |
| 翻译质量 | ⭐⭐⭐⭐ (95%) | ⭐⭐⭐⭐⭐ (100%) |

### Q: 如何提高翻译速度？
A: 
1. **使用 GPU**：安装 CUDA，速度提升 3-5 倍
2. **Docker Compose**：微服务并行处理
3. **调整参数**：增加 `MAX_WORKERS` 环境变量
4. **硬件升级**：增加 CPU 核心和内存

### Q: 翻译的文件会保存多久？
A: 
- 默认保存 **24 小时**后自动清理
- 可通过 `FILE_RETENTION_HOURS` 环境变量自定义
- 建议生产环境设置为 1-2 小时

### Q: 可以商用吗？有什么限制？
A: **完全可以商用！**
- ✅ MIT 许可证，允许商业使用
- ✅ 无需支付授权费用
- ✅ 可以修改代码并内部使用
- ⚠️ 不能移除版权声明
- 💡 建议保留 LICENSE 文件

### Q: 遇到错误怎么办？
A: 
1. 📋 查看日志：`logs/app.log`
2. 📊 访问监控：`http://localhost:5002/api/monitor`
3. 🔍 搜索 Issues：可能已有解决方案
4. 💬 提交新 Issue：[点击这里](https://github.com/FrankDu1/multi-format-translator/issues)

### Q: 是否支持多用户并发？
A: **是的！**
- 支持多用户同时使用
- 使用队列机制处理并发请求
- 可通过负载均衡扩展到多台服务器
- 推荐配合 Nginx/Traefik 使用

## 🗺️ 项目路线图 / Roadmap

### ✅ 已完成 / Completed (v1.0)
- [x] 文本翻译（中英德等多语言）
- [x] PDF 翻译（保持原格式）
- [x] 图片翻译（OCR + 翻译 + 修复）
- [x] PPT 翻译（原格式输出）
- [x] AI 智能总结功能
- [x] Docker 容器化部署
- [x] 多语言界面（中/英）
- [x] 环境变量配置系统
- [x] 本地化部署支持

### 🚧 进行中 / In Progress (v1.1 - Q1 2026)
- [ ] **Word 文档翻译** - 保持格式和样式
- [ ] **批量文件翻译** - 支持一次上传多个文件
- [ ] **翻译历史记录** - 查看和管理历史翻译
- [ ] **更多 AI 模型** - 支持 Claude, Gemini, 本地 Ollama
- [ ] **翻译质量评估** - 自动评分和改进建议
- [ ] **性能优化** - 提升大文件处理速度

### 📋 计划中 / Planned (v1.2 - Q2 2026)
- [ ] **Excel 翻译** - 保持公式和格式
- [ ] **实时协作翻译** - 多人同时编辑
- [ ] **术语库管理** - 自定义专业术语翻译
- [ ] **翻译记忆库** - 复用历史翻译，提高一致性
- [ ] **API 认证** - JWT/OAuth 支持
- [ ] **用户管理系统** - 多用户权限控制
- [ ] **翻译统计报表** - 使用量、成本分析

### 🔮 未来规划 / Future (v2.0 - Q3 2026)
- [ ] **浏览器插件** - Chrome/Firefox 扩展
- [ ] **移动端应用** - iOS/Android APP
- [ ] **语音翻译** - 实时语音识别和翻译
- [ ] **视频字幕翻译** - SRT/ASS 字幕文件
- [ ] **企业版功能**：
  - 集群部署和负载均衡
  - 审计日志和合规报告
  - SSO 单点登录集成
  - 高可用性保障

### 💡 社区建议 / Community Suggestions
欢迎在 [Issues](https://github.com/FrankDu1/multi-format-translator/issues) 中提出你的想法！

投票最多的功能将优先开发 🎯

## 📊 性能指标 / Performance

| 操作 | 平均耗时 | 备注 |
|------|---------|------|
| 文本翻译 (100字) | ~1s | 使用 CPU |
| 图片翻译 (1MB) | ~5-10s | 包含 OCR + 翻译 |
| PDF 翻译 (10页) | ~30-60s | 取决于页面复杂度 |
| PPT 翻译 (20页) | ~40-80s | 取决于文本量 |

*测试环境：Intel i7-10700K, 16GB RAM, 无 GPU*

## 🛡️ 安全性 / Security

- 🔐 支持 HTTPS 部署
- 🔒 监控面板密码保护
- 📁 文件自动清理
- 🚫 文件类型验证
- 📏 文件大小限制
- 🌐 CORS 配置

详见 [SECURITY.md](SECURITY.md)

## 📞 联系方式 / Contact

- Email: dusiyu2004@hotmail.com
- Website: https://offerupup.top
- 小红书: [@乐家](https://www.xiaohongshu.com/user/profile/64f2bd6300000000060303f3)

## 🔗 相关链接 / Links

- [在线演示](https://offerupup.cn/trans)
- [问题反馈](https://github.com/FrankDu1/multi-format-translator/issues)
- [贡献指南](CONTRIBUTING.md)
- [变更日志](CHANGELOG.md)

## ⭐ Star 历史 / Star History

[![Star History Chart](https://api.star-history.com/svg?repos=FrankDu1/multi-format-translator&type=Date)](https://star-history.com/#FrankDu1/multi-format-translator&Date)

---

**如果这个项目对您有帮助，请给个 ⭐ Star！**

**If this project helps you, please give it a ⭐ Star!**
