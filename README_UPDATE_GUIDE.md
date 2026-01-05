# README 更新建议

## 在README.md顶部添加的Badge

将以下代码添加到README.md的顶部（替换现有的badge部分）：

```markdown
[![CI](https://github.com/你的用户名/multi-format-translator/actions/workflows/ci.yml/badge.svg)](https://github.com/你的用户名/multi-format-translator/actions)
[![Docker Build](https://github.com/你的用户名/multi-format-translator/actions/workflows/docker-build.yml/badge.svg)](https://github.com/你的用户名/multi-format-translator/actions/workflows/docker-build.yml)
[![Release](https://img.shields.io/github/v/release/你的用户名/multi-format-translator)](https://github.com/你的用户名/multi-format-translator/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/你的用户名/translator-api)](https://hub.docker.com/r/你的用户名/translator-api)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/你的用户名/multi-format-translator?style=social)](https://github.com/你的用户名/multi-format-translator/stargazers)
```

## 添加Docker Hub快速启动部分

在"快速开始"章节前添加：

```markdown
## 🐳 Docker Hub快速部署（推荐）

### 使用预构建镜像

```bash
# 1. 创建配置文件
cp .env.example .env

# 2. 使用Docker Hub镜像启动
docker-compose up -d

# 3. 访问服务
# 打开浏览器: http://localhost:5001
```

**镜像地址：**
- Frontend: `你的用户名/translator-frontend:latest`
- API: `你的用户名/translator-api:latest`
- OCR: `你的用户名/translator-ocr:latest`
- Inpaint: `你的用户名/translator-inpaint:latest`

**优势：**
- ⚡ 无需构建，直接使用
- 🔄 自动更新到最新版本
- 📦 统一的生产环境
```

## 修改docker-compose.yml使用Docker Hub镜像

创建一个新的 `docker-compose.hub.yml`：

```yaml
version: '3.8'

services:
  ocr:
    image: 你的用户名/translator-ocr:latest
    # 其他配置保持不变...

  inpaint:
    image: 你的用户名/translator-inpaint:latest
    # 其他配置保持不变...

  api:
    image: 你的用户名/translator-api:latest
    # 其他配置保持不变...

  frontend:
    image: 你的用户名/translator-frontend:latest
    # 其他配置保持不变...
```

然后在README中说明：

```markdown
### 使用方式

**使用Docker Hub镜像（推荐）：**
```bash
docker-compose -f docker-compose.hub.yml up -d
```

**从源码构建：**
```bash
docker-compose up -d --build
```
```

## 添加徽章说明

在README底部添加：

```markdown
---

## 📊 项目状态

- ✅ 持续集成：自动代码检查和测试
- ✅ Docker构建：自动构建多平台镜像
- ✅ 自动发布：Tag自动创建Release
- ✅ 生产就绪：经过充分测试的Docker镜像

**查看构建状态：** [GitHub Actions](https://github.com/你的用户名/multi-format-translator/actions)
```
