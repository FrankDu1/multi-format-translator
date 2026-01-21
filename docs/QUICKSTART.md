# 快速入门指南 / Quick Start Guide

本指南将帮助你在几分钟内启动并运行整个翻译服务。

## 🎯 目标

完成本指南后，你将拥有一个完整运行的本地翻译服务，包括：
- ✅ OCR 文字识别服务
- ✅ 图像修复服务
- ✅ 翻译 API 服务
- ✅ Web 前端界面

## 📋 前置要求

- Python 3.8 或更高版本
- pip (Python 包管理器)
- 至少 4GB RAM
- (可选) NVIDIA GPU + CUDA 用于加速

## 🚀 三步启动

### 步骤 1: 下载项目

```bash
git clone https://github.com/FrankDu1/multi-format-translator.git
cd multi-format-translator
```

### 步骤 2: 配置环境（可选）

默认配置可直接运行。如需自定义，复制环境变量模板：

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置（可选）
# Windows: notepad .env
# Linux/Mac: nano .env
```

### 步骤 3: 启动服务

**Windows 用户：**
```cmd
# 双击运行或命令行执行
manage-services.bat
# 然后选择 1 (启动所有服务)
```

**Linux/Mac 用户：**
```bash
chmod +x start-all-dev.sh
./start-all-dev.sh
```

**或使用 Docker（最简单）：**
```bash
docker-compose up -d
```

## ✅ 验证安装

1. 打开浏览器访问：http://localhost:5001
2. 你应该看到翻译工具的主界面
3. 尝试翻译一些文本或上传图片测试

## 🔍 服务地址

启动后，以下服务将可用：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端** | http://localhost:5001 | Web 界面 |
| API | http://localhost:5002 | 翻译 API |
| OCR | http://localhost:8899 | 文字识别 |
| Inpaint | http://localhost:8900 | 图像修复 |

## 🛠️ 常见问题

### 端口已被占用

如果看到端口冲突错误，修改 `.env` 文件中的端口：

```bash
API_PORT=5002      # 改为其他端口，如 5003
OCR_PORT=8899      # 改为其他端口，如 8898
INPAINT_PORT=8900  # 改为其他端口，如 8901
FRONTEND_PORT=5001 # 改为其他端口，如 5000
```

### 依赖安装失败

如果 pip 安装失败，尝试使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### GPU 相关错误

如果没有 GPU，系统会自动回退到 CPU 模式，只是速度会慢一些。

## 📚 下一步

- 查看 [README.md](README.md) 了解更多功能
- 阅读 [配置文档](.env.example) 自定义设置
- 访问 [贡献指南](CONTRIBUTING.md) 参与开发

## 🆘 需要帮助？

- 📖 查看完整文档：[README.md](README.md)
- 🐛 报告问题：[GitHub Issues](https://github.com/FrankDu1/multi-format-translator/issues)
- 💬 讨论交流：[GitHub Discussions](https://github.com/FrankDu1/multi-format-translator/discussions)

---

**祝你使用愉快！** 🎉
