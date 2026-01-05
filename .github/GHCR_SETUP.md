# GitHub Container Registry (GHCR) 使用指南

## 🎯 为什么使用GHCR？

✅ **完全免费** - 无限制的公开镜像存储  
✅ **无需配置** - 自动使用 `GITHUB_TOKEN`，无需额外Secrets  
✅ **权限集成** - 与GitHub仓库权限自动同步  
✅ **快速稳定** - GitHub官方基础设施  

## 📦 镜像地址格式

```
ghcr.io/你的用户名/仓库名/服务名:标签
```

**示例：**
```
ghcr.io/frankdu1/multi-format-translator/translator-api:latest
ghcr.io/frankdu1/multi-format-translator/translator-api:v1.0.0
```

## 🚀 使用方式

### 1. 推送代码触发构建

```bash
git push origin main
```

GitHub Actions会自动：
1. 构建Docker镜像
2. 推送到GHCR
3. 自动打标签

### 2. 查看构建的镜像

访问：**GitHub仓库 → Packages（右侧）**

你会看到：
- `translator-frontend`
- `translator-api`
- `translator-ocr`
- `translator-inpaint`

### 3. 设置镜像为公开（重要！）

**为什么要设置为公开？**
- 其他人可以直接拉取，无需登录
- 你自己拉取也更方便

**操作步骤：**
1. 点击任意一个包（如 `translator-api`）
2. 右侧找到 **Package settings**
3. 拉到底部，点击 **Change visibility**
4. 选择 **Public**
5. 输入仓库名确认
6. 点击 **I understand the consequences, change package visibility**

对所有4个包重复上述步骤。

### 4. 拉取镜像

**公开镜像（推荐）：**
```bash
# 无需登录，直接拉取
docker pull ghcr.io/你的用户名/multi-format-translator/translator-api:latest
```

**私有镜像：**
```bash
# 1. 创建GitHub Personal Access Token
# Settings → Developer settings → Personal access tokens → Tokens (classic)
# Generate new token → 勾选 read:packages

# 2. 登录GHCR
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 3. 拉取镜像
docker pull ghcr.io/你的用户名/multi-format-translator/translator-api:latest
```

## 🐳 更新docker-compose.yml

### 方式1：创建新文件 `docker-compose.ghcr.yml`

```yaml
version: '3.8'

services:
  ocr:
    image: ghcr.io/你的用户名/multi-format-translator/translator-ocr:latest
    container_name: translator-ocr
    ports:
      - "${OCR_PORT:-8899}:8899"
    # ... 其他配置保持不变

  inpaint:
    image: ghcr.io/你的用户名/multi-format-translator/translator-inpaint:latest
    # ...

  api:
    image: ghcr.io/你的用户名/multi-format-translator/translator-api:latest
    # ...

  frontend:
    image: ghcr.io/你的用户名/multi-format-translator/translator-frontend:latest
    # ...
```

**使用：**
```bash
docker-compose -f docker-compose.ghcr.yml up -d
```

### 方式2：直接修改原文件

将 `build` 部分改为 `image`：

```yaml
# 修改前
services:
  api:
    build:
      context: ./translator_api
      dockerfile: Dockerfile

# 修改后
services:
  api:
    image: ghcr.io/你的用户名/multi-format-translator/translator-api:latest
```

## 📊 查看镜像信息

### 在GitHub上

1. 访问包页面
2. 查看：
   - 下载次数
   - 所有标签
   - 镜像大小
   - 推送历史

### 命令行

```bash
# 查看镜像信息
docker images ghcr.io/你的用户名/multi-format-translator/*

# 查看镜像详情
docker inspect ghcr.io/你的用户名/multi-format-translator/translator-api:latest
```

## 🔧 高级配置

### 自动删除旧标签

在 `.github/workflows/docker-build.yml` 中添加：

```yaml
- name: 清理旧镜像
  uses: actions/delete-package-versions@v4
  with:
    package-name: 'translator-api'
    package-type: 'container'
    min-versions-to-keep: 10
    delete-only-untagged-versions: true
```

### 添加镜像标签

在工作流中自定义标签：

```yaml
tags: |
  type=ref,event=branch
  type=ref,event=pr
  type=semver,pattern={{version}}
  type=semver,pattern={{major}}.{{minor}}
  type=sha,prefix={{branch}}-
  type=raw,value=latest,enable={{is_default_branch}}
```

### 镜像缓存优化

已配置GitHub Actions缓存：

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

这会大幅加速后续构建（从20分钟降到5分钟）。

## 📈 监控和维护

### 查看包统计

访问：**GitHub仓库 → Insights → Traffic**

可以看到：
- 包下载次数
- 唯一访问者
- 流量来源

### 定期清理

```bash
# 删除本地旧镜像
docker image prune -a

# 删除GitHub上的旧版本
# 在包设置中配置保留策略
```

## 🎉 优势总结

| 特性 | GHCR | Docker Hub (免费版) |
|------|------|-------------------|
| 公开镜像存储 | ✅ 无限制 | ✅ 无限制 |
| 私有镜像 | ✅ 无限制 | ❌ 仅1个 |
| 拉取速率限制 | ✅ 无限制 | ⚠️ 100次/6小时 |
| 需要配置Secrets | ❌ 不需要 | ✅ 需要 |
| 与GitHub集成 | ✅ 原生集成 | ❌ 需要单独配置 |
| 权限管理 | ✅ 自动同步 | ❌ 独立管理 |

## 🔍 故障排查

### 1. "permission denied" 错误

**原因：** 工作流没有写入packages权限

**解决：**
```yaml
permissions:
  contents: read
  packages: write  # 添加这行
```

### 2. 镜像拉取失败 (404)

**原因：** 镜像是私有的

**解决：**
1. 设置为公开（推荐）
2. 或登录后拉取

### 3. 构建失败

**检查：**
1. GitHub Actions日志
2. Dockerfile语法
3. 依赖是否可访问

### 4. 标签冲突

**原因：** 多个workflow同时推送

**解决：**
```yaml
concurrency:
  group: docker-build-${{ github.ref }}
  cancel-in-progress: true
```

## 📚 参考资料

- [GitHub Packages文档](https://docs.github.com/en/packages)
- [GHCR使用指南](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions文档](https://docs.github.com/en/actions)

---

## 🎯 快速命令参考

```bash
# 拉取镜像
docker pull ghcr.io/你的用户名/仓库名/服务名:latest

# 登录GHCR（如果是私有）
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 启动服务
docker-compose -f docker-compose.ghcr.yml up -d

# 查看日志
docker-compose logs -f

# 更新镜像
docker-compose pull
docker-compose up -d
```
