# GitHub Actions Docker自动构建配置指南

## 📋 概述

项目已配置3个GitHub Actions工作流：

1. **docker-build.yml** - 自动构建和发布（push到main/develop分支时触发）
2. **docker-publish-manual.yml** - 手动发布（可选择特定服务和标签）
3. **ci.yml** - 持续集成测试（代码检查和构建测试）

## 🔧 配置步骤

### 1. 配置GitHub Secrets

进入你的GitHub仓库：**Settings → Secrets and variables → Actions → New repository secret**

添加以下secrets：

| Secret名称 | 说明 | 示例 |
|-----------|------|------|
| `DOCKER_USERNAME` | Docker Hub用户名 | `yourname` |
| `DOCKER_PASSWORD` | Docker Hub访问令牌 | `dckr_pat_xxx...` |

**如何获取Docker Hub访问令牌：**

1. 登录 https://hub.docker.com/
2. Account Settings → Security → New Access Token
3. 输入Token名称（如 `github-actions`）
4. 复制生成的Token（只显示一次！）

### 2. 启用GitHub Actions

1. 进入仓库 **Actions** 标签
2. 如果提示启用，点击 **"I understand my workflows, go ahead and enable them"**
3. 现在工作流已启用

## 🚀 使用方式

### 自动构建（推荐）

**触发条件：**
- Push代码到 `main` 或 `develop` 分支
- 创建版本标签（如 `v1.0.0`）

**流程：**
```bash
# 1. 提交代码
git add .
git commit -m "feat: 添加新功能"
git push origin main

# 2. GitHub Actions自动触发
# - 构建4个Docker镜像
# - 推送到Docker Hub
# - 运行健康检查
# - 创建Release（如果是tag）
```

**查看构建状态：**
- 访问 GitHub仓库 → Actions
- 查看正在运行的workflow

### 手动构建

**触发方式：**

1. 进入仓库 **Actions** 标签
2. 选择 **"Manual Docker Publish"**
3. 点击 **"Run workflow"**
4. 填写参数：
   - **服务**：选择要构建的服务（或all构建全部）
   - **标签**：指定镜像标签（如 `v1.0.0`、`latest`）
   - **平台**：选择目标平台（amd64、arm64或两者）
5. 点击 **"Run workflow"**

**示例：只构建API服务**
```
Service: api
Tag: test-version
Platforms: linux/amd64
```

### 版本发布

**创建带标签的Release：**

```bash
# 1. 创建并推送tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 2. GitHub Actions自动：
# - 构建所有镜像，标签为 v1.0.0 和 latest
# - 运行测试
# - 创建GitHub Release
# - 附带Docker拉取命令
```

## 📦 镜像标签策略

工作流自动生成以下标签：

| 触发事件 | 生成的标签 |
|---------|-----------|
| Push到main分支 | `latest`, `main` |
| Push到develop分支 | `develop` |
| Pull Request | `pr-123` |
| Tag v1.2.3 | `v1.2.3`, `1.2`, `1`, `latest` |
| Commit SHA | `main-abc1234` |

**示例：**
```bash
# Tag v1.2.3 会生成：
yourname/translator-api:v1.2.3
yourname/translator-api:1.2
yourname/translator-api:1
yourname/translator-api:latest
```

## 🐳 使用构建的镜像

### 拉取镜像

```bash
# 拉取最新版本
docker pull yourname/translator-frontend:latest
docker pull yourname/translator-api:latest
docker pull yourname/translator-ocr:latest
docker pull yourname/translator-inpaint:latest

# 拉取特定版本
docker pull yourname/translator-api:v1.0.0
```

### 修改docker-compose.yml

修改项目的 `docker-compose.yml`，使用Docker Hub镜像：

```yaml
services:
  api:
    image: yourname/translator-api:latest  # 替换build配置
    # build:
    #   context: ./translator_api
    #   dockerfile: Dockerfile
    container_name: translator-api
    # ... 其他配置保持不变

  ocr:
    image: yourname/translator-ocr:latest
    # ... 

  inpaint:
    image: yourname/translator-inpaint:latest
    # ...

  frontend:
    image: yourname/translator-frontend:latest
    # ...
```

然后直接启动：

```bash
docker-compose up -d
```

## 🔍 故障排查

### 构建失败

**查看日志：**
1. GitHub仓库 → Actions
2. 点击失败的workflow
3. 查看具体步骤的错误信息

**常见问题：**

1. **Docker Hub认证失败**
   - 检查 `DOCKER_USERNAME` 和 `DOCKER_PASSWORD` 是否正确配置
   - 确保使用的是Access Token，不是密码

2. **构建超时**
   - GitHub免费版有时间限制
   - 考虑减少并行构建数量

3. **磁盘空间不足**
   - Actions runner磁盘空间有限
   - 工作流已配置缓存策略

### 推送失败

**检查Docker Hub配额：**
- 免费账户有拉取速率限制
- 考虑升级到Pro账户

### 健康检查失败

**调试方法：**
```yaml
# 在workflow中添加更多日志
- name: 📋 查看日志
  if: failure()
  run: |
    docker-compose logs
```

## 📊 工作流说明

### docker-build.yml

**功能：**
- ✅ 多服务并行构建
- ✅ 自动标签管理
- ✅ 多平台支持（amd64 + arm64）
- ✅ 构建缓存优化
- ✅ 健康检查测试
- ✅ 自动创建Release

**运行时间：**
- 首次构建：约20-30分钟
- 后续构建（有缓存）：约10-15分钟

### docker-publish-manual.yml

**适用场景：**
- 测试特定版本
- 快速修复发布
- 单服务更新
- 多平台测试

### ci.yml

**功能：**
- 代码质量检查
- 构建测试（不推送）
- Pull Request检查

## 🎯 最佳实践

### 1. 分支策略

```
main (生产)
  ↑
develop (开发)
  ↑
feature/* (功能分支)
```

**工作流：**
1. 在 `feature/*` 分支开发
2. 合并到 `develop` 测试
3. 测试通过后合并到 `main`
4. 打tag发布版本

### 2. 版本命名

**使用语义化版本：**
```bash
v1.0.0  # 主版本.次版本.修订版
v1.1.0  # 新功能
v1.1.1  # Bug修复
```

### 3. 镜像大小优化

**在Dockerfile中：**
- 使用多阶段构建
- 清理不必要的文件
- 使用 `.dockerignore`

### 4. 安全性

**保护secrets：**
- 不在日志中输出secrets
- 定期轮换Access Token
- 限制Token权限

## 📈 监控和通知

### GitHub Actions Badge

添加到README.md：

```markdown
[![Docker Build](https://github.com/yourname/multi-format-translator/actions/workflows/docker-build.yml/badge.svg)](https://github.com/yourname/multi-format-translator/actions/workflows/docker-build.yml)
```

### Docker Hub自动构建统计

访问：https://hub.docker.com/r/yourname/translator-api

查看：
- 拉取次数
- 标签列表
- 镜像大小

## 🚀 下一步

1. **推送代码测试工作流**
   ```bash
   git add .github/
   git commit -m "ci: 添加Docker自动构建工作流"
   git push origin main
   ```

2. **监控首次构建**
   - 访问 Actions 标签
   - 查看构建进度
   - 等待约20-30分钟

3. **验证镜像**
   ```bash
   docker pull yourname/translator-api:latest
   docker run --rm yourname/translator-api:latest --version
   ```

4. **更新项目文档**
   - 在README.md中添加Docker Hub链接
   - 更新部署文档

## 🎉 完成！

现在你的项目已经配置了完整的CI/CD流程：
- ✅ 自动构建Docker镜像
- ✅ 自动发布到Docker Hub
- ✅ 自动创建GitHub Release
- ✅ 健康检查测试
- ✅ 多平台支持

每次推送代码都会自动触发构建，无需手动操作！
