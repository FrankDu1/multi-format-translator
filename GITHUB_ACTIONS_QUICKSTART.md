# 🚀 GitHub Actions Docker 快速配置

## ⚡ 2步完成自动构建（无需配置Secrets！）

### 步骤1：推送代码

```bash
# 提交workflow文件
git add .github/
git commit -m "ci: 添加Docker自动构建"
git push origin main
```

**说明：** 使用GitHub Container Registry (GHCR)，无需配置任何Secrets！

---

### 步骤2：查看构建

访问：**GitHub仓库 → Actions**

等待构建完成（约15-20分钟）

---

## 🎯 触发方式

### 自动触发

**Push到main/develop分支：**
```bash
git push origin main
# → 自动构建所有4个Docker镜像
# → 推送到Docker Hub
```

**创建版本Tag：**
```bash
git tag v1.0.0
git push origin v1.0.0
# → 构建镜像，标签为 v1.0.0 和 latest
# → 自动创建GitHub Release
```

### 手动触发

1. 访问：**Actions → Manual Docker Publish**
2. 点击：**Run workflow**
3. 选择服务和标签
4. 点击：**Run workflow**

---

## 🐳 使用构建的镜像

### 拉取镜像

```bash
docker pull ghcr.io/你的用户名/multi-format-translator/translator-frontend:latest
docker pull ghcr.io/你的用户名/multi-format-translator/translator-api:latest
docker pull ghcr.io/你的用户名/multi-format-translator/translator-ocr:latest
docker pull ghcr.io/你的用户名/multi-format-translator/translator-inpaint:latest
```

**注意：** 首次拉取需要登录GitHub Container Registry：

```bash
# 创建GitHub Personal Access Token (PAT)
# Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
# 勾选 read:packages 权限

# 登录GHCR
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 然后拉取镜像
docker pull ghcr.io/你的用户名/multi-format-translator/translator-api:latest
```

**公开镜像（推荐）：**
- 在GitHub仓库的 Packages 中，将镜像设置为 Public
- 这样任何人都可以直接拉取，无需登录

### 启动服务

```bash
# 直接使用Docker Hub镜像
docker-compose up -d
```

---

## 📋 生成的镜像标签

| 操作 | 镜像地址 | 标签 |
|------|---------|------|
| Push到main | `ghcr.io/你的用户名/仓库名/translator-api` | `latest`, `main` |
| Push到develop | `ghcr.io/你的用户名/仓库名/translator-api` | `develop` |
| Tag v1.2.3 | `ghcr.io/你的用户名/仓库名/translator-api` | `v1.2.3`, `1.2`, `1`, `latest` |

---

## 🔍 故障排查

### 权限问题

如果看到 "permission denied" 错误，检查：

✅ 工作流文件中添加了 `permissions` 配置：
```yaml
permissions:
  contents: read
  packages: write
```

### 镜像拉取失败

✅ 确认镜像已设置为 Public：
1. 访问 GitHub 仓库
2. 右侧找到 Packages
3. 点击包名
4. Package settings → Change visibility → Public

### 查看构建日志

✅ GitHub → Actions → 选择失败的workflow → 查看详细日志

---

## 🎉 完成！

现在每次push代码都会自动：
- ✅ 构建Docker镜像
- ✅ 推送到GitHub Container Registry
- ✅ 运行测试
- ✅ 创建Release（如果是tag）

**优势：**
- 🆓 完全免费，无需Docker Hub账号
- 🔒 与GitHub仓库权限集成
- 🚀 无需配置额外的Secrets
- 📦 无限制的公开镜像存储

**详细文档：** 查看 `.github/DOCKER_SETUP.md`
